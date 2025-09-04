from collections.abc import Iterable
import collections
import urllib.parse
import uuid

import pendulum
import zope.formlib.form
import zope.formlib.widgets

from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
import zeit.cms.browser.form
import zeit.cms.browser.view
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.content.image.browser.imagegroup
import zeit.content.image.image
import zeit.content.image.interfaces


# This is just a dummy to get into the addcentral sidebar
class IImageUploadImage(zeit.content.image.interfaces.IImageGroup):
    pass


IImageUploadImage.setTaggedValue('zeit.cms.addform', 'upload-images')
IImageUploadImage.setTaggedValue('zeit.cms.title', _('Image (new)'))
IImageUploadImage.setTaggedValue('zeit.cms.type', None)


@zope.interface.implementer(zeit.cms.browser.interfaces.IHideContextViews)
class UploadForm(zeit.cms.browser.view.Base, zeit.content.image.browser.form.CreateImageMixin):
    title = _('Upload images')

    def __call__(self):
        if self.request.method == 'POST':
            return self.handle_post()
        return super().__call__()

    def action(self):
        return self.url(self.context, '@@upload-images')

    def from_name(self):
        return self.context.__name__

    def handle_post(self):
        # Since self.context is potentially checked out, we cannot rely on self.context.__parent__
        target = zeit.cms.interfaces.ICMSContent(self.context.uniqueId)

        in_folder = zeit.cms.repository.interfaces.IFolder.providedBy(target)
        # If we upload in a folder, we don't want to go up
        if not in_folder:
            target = target.__parent__

        files = self.request.form.get('files', None)
        if not files:
            self.send_message(_('Please upload at least one image'), type='error')
            return super().__call__()

        if not isinstance(files, Iterable):
            files = (files,)

        results = []
        for file in files:
            result = self._upload_imagegroup(file, target)
            results.append(result)

        params = {'files': results}
        if not in_folder:
            renameable = zeit.cms.repository.interfaces.IAutomaticallyRenameable(self.context)
            if renameable.renameable:
                # This is a new article, so don't use it's (temporary name)
                if renameable.rename_to:
                    # … unless the user already gave it a name
                    params['from'] = renameable.rename_to
            else:
                params['from'] = self.context.__name__
        url = self.url(target, '@@edit-images') + '?' + urllib.parse.urlencode(params, doseq=True)
        if self.request.getHeader('X-Requested-With') == 'XMLHttpRequest':
            return url
        self.redirect(url, status=303)

    def _upload_imagegroup(self, file, parent):
        imagegroup = zeit.content.image.imagegroup.ImageGroup()
        image = self.create_image(file)
        viewport = next(iter(zeit.content.image.interfaces.VIEWPORT_SOURCE))
        imagegroup.master_images = ((viewport, image.__name__),)
        name = f'{uuid.uuid4()}.tmp'
        zeit.cms.repository.interfaces.IAutomaticallyRenameable(imagegroup).renameable = True
        parent[name] = imagegroup
        imagegroup[image.__name__] = image
        return name


def get_image_name(base_name, pos, others):
    if others == 0:
        suffix = ''
    elif others < 9:
        suffix = f'-{pos}'
    else:
        suffix = f'-{pos:02}'
    return base_name + '-bild' + suffix


class ImageName:
    def __init__(self, provider, base_name, pos):
        self.provider = provider
        self.base_name = base_name
        self.pos = pos

    def __str__(self):
        total_count = self.provider.total_counts[self.base_name]
        return get_image_name(self.base_name, self.pos, total_count - 1)


class ImageNameProvider:
    """A helper class for producing image names for given base names (for example article names).
    This correctly counts existing images and new images to add and generates unique file names.

    ImageNameProvider.get returns a dynamic ImageName object that can be converted to str.
    Through that, an ImageName object can also consider images that were added after it.

    ImageNameProvider does not handle holes in image name sequences.
    For example, if article-bild-1 and article-bild-3 exist, suggested names for images for article
    would be article-bild-2, article-bild-3 and so on.
    """

    def __init__(self, container):
        self.container = container
        self.container_counts = collections.Counter()
        self.total_counts = collections.Counter()

    def _init_from_container(self, base_name):
        # Two digits
        if get_image_name(base_name, 1, 9) in self.container:
            count = 1
            while get_image_name(base_name, count + 1, 9) in self.container:
                count += 1
        # One digit
        elif get_image_name(base_name, 1, 1) in self.container:
            count = 1
            while get_image_name(base_name, count + 1, 1) in self.container:
                count += 1
        # No digit
        elif get_image_name(base_name, 1, 0) in self.container:
            count = 1
        else:
            count = 0
        self.total_counts[base_name] = self.container_counts[base_name] = count

    def get(self, base_name):
        if base_name not in self.total_counts:
            self._init_from_container(base_name)
        self.total_counts[base_name] += 1
        return ImageName(self, base_name, self.total_counts[base_name])


@zope.interface.implementer(zeit.cms.browser.interfaces.IHideContextViews)
class EditForm(zeit.cms.browser.view.Base):
    title = _('Edit images')

    _files = ()
    _errors = {}

    def __call__(self):
        self._errors = {}
        if self.request.method == 'POST':
            self._files = tuple(self._parse_post_request())
            if 'cancel' in self.request.form:
                return self.handle_cancel()
            return self.handle_submit()

        self._files = tuple(self._parse_get_request())
        return super().__call__()

    def handle_cancel(self):
        for file in self._files:
            del self.context[file['tmp_name']]
        self.redirect(self.url(name=''), status=303)

    def prepare_publish(self, image):
        info = IPublishInfo(image)
        info.date_last_published_semantic = pendulum.now('UTC')
        info.corrected = True
        info.edited = True
        semantic = ISemanticChange(image)
        semantic.last_semantic_change = info.date_last_published_semantic

    def handle_submit(self):
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(self.context)
        taken_names = set()
        for file in self._files:
            if (
                file['target_name'] != file['tmp_name'] and file['target_name'] in self.context
            ) or (file['target_name'] in taken_names):
                self._errors[file['tmp_name']] = _('File name is already in use')
            taken_names.add(file['target_name'])

        if self._errors:
            return super().__call__()

        publish = self.request.form.get('publish', None) == 'true'
        for file in self._files:
            tmp_name = file['tmp_name']
            name = file['target_name']
            # Since tmp_name ends with '.tmp', and target_name is normalized
            # (which replaces the '.' with '-'), the two always differ.
            renamer.renameItem(tmp_name, name)
            with zeit.cms.checkout.helper.checked_out(
                self.context[name], temporary=False, raise_if_error=True
            ) as imagegroup:
                metadata = zeit.content.image.interfaces.IImageMetadata(imagegroup)
                metadata.copyright = (
                    None,
                    'Andere',
                    file['copyright'],
                    None,
                    False,
                )
                metadata.title = file['title']
                metadata.caption = file['caption']
                zeit.cms.repository.interfaces.IAutomaticallyRenameable(
                    imagegroup
                ).renameable = False
                if publish:
                    self.prepare_publish(imagegroup)
            if publish:
                IPublish(self.context[name]).publish(background=False)

        if len(self._files) == 1:
            route = '@@variant.html'
            if self.request.form.get('open', None) == 'true':
                route = '@@checkout?came_from=variant.html'
            url = self.url(self.context[self._files[0]['target_name']], name=route)
        else:
            url = self.url(name='')

        if self.request.getHeader('X-Requested-With') == 'XMLHttpRequest':
            return url
        self.redirect(url, status=303)

    def _parse_get_request(self):
        from_name = self.request.form.get('from', None)
        filenames = self.request.form.get('files', ())
        if isinstance(filenames, str):
            filenames = (filenames,)

        name_provider = ImageNameProvider(self.context)
        for tmp_name in filenames:
            imggroup = self.context[tmp_name]

            meta = imggroup[imggroup.master_image].getXMPMetadata()

            name_base = None
            if from_name:
                name_base = from_name
            elif meta['title'] is not None:
                name_base = zeit.cms.interfaces.normalize_filename(meta['title'])

            if name_base:
                name = name_provider.get(name_base)
            else:
                name = ''

            yield {
                'tmp_name': tmp_name,
                'target_name': name,
                'title': meta['title'],
                'copyright': meta['copyright'],
                'caption': meta['caption'],
                'thumbnail': self.url(imggroup, 'thumbnail'),
            }

    def _parse_post_request(self):
        index = 0
        while f'tmp_name[{index}]' in self.request.form:
            tmp_name = self.request.form[f'tmp_name[{index}]']
            target_name = zeit.cms.interfaces.normalize_filename(
                self.request.form[f'target_name[{index}]']
            )
            yield {
                'tmp_name': tmp_name,
                'target_name': target_name,
                'title': self.request.form[f'title[{index}]'],
                'copyright': self.request.form[f'copyright[{index}]'],
                'caption': self.request.form[f'caption[{index}]'],
                'thumbnail': self.url(self.context[tmp_name], 'thumbnail'),
            }
            index += 1

    def rows(self):
        for file in self._files:
            res = dict(file)
            res['error'] = self._errors.get(file['tmp_name'], False)
            yield res
