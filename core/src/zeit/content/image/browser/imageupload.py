from collections.abc import Iterable
import collections
import os.path
import urllib.parse
import uuid

from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import zope.event
import zope.formlib.form
import zope.formlib.widgets
import zope.lifecycleevent

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish
import zeit.cms.browser.form
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
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

    def accepted_mime_types(self):
        return ','.join(zeit.content.image.interfaces.AVAILABLE_MIME_TYPES)

    def handle_post(self):
        files = self.request.form.get('files', None)
        if not files:
            return self._report_user_error(_('Please upload at least one image'))

        if not isinstance(files, Iterable) or isinstance(files, str):
            files = (files,)

        mdb = zope.component.getUtility(zeit.content.image.interfaces.IMDB)
        files = tuple(
            mdb.get_body(file.replace('mdb:', ''))
            if isinstance(file, str) and file.startswith('mdb:')
            else file
            for file in files
        )

        try:
            for file in files:
                zeit.content.image.browser.interfaces.is_image(file)
        except zope.schema.ValidationError as e:
            return self._report_user_error(e.doc())

        target = zeit.content.image.browser.interfaces.IUploadTarget(self.context)
        params = {'files': tuple(self._upload_imagegroup(file, target) for file in files)}

        url = self.url(name='@@edit-images') + '?' + urllib.parse.urlencode(params, doseq=True)
        if self._is_xhr_request():
            return url
        self.redirect(url, status=303)

    def _is_xhr_request(self):
        return self.request.getHeader('X-Requested-With') == 'XMLHttpRequest'

    def _report_user_error(self, error_message):
        self.request.response.setStatus(400)
        if self._is_xhr_request():
            return zope.i18n.translate(error_message, context=self.request)
        else:
            self.send_message(error_message, type='error')
            return super().__call__()

    def _upload_imagegroup(self, file, parent):
        imagegroup = zeit.content.image.imagegroup.ImageGroup()
        image = self.create_image(file)
        viewport = next(iter(zeit.content.image.interfaces.VIEWPORT_SOURCE))
        imagegroup.master_images = ((viewport, image.__name__),)
        name = f'{uuid.uuid4()}.tmp'
        zeit.cms.repository.interfaces.IAutomaticallyRenameable(imagegroup).renameable = True
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(imagegroup))
        parent[name] = imagegroup
        imagegroup[image.__name__] = image
        return name


@grok.adapter(zeit.cms.interfaces.ICMSContent)
@grok.implementer(zeit.content.image.browser.interfaces.IUploadTarget)
def default_target(context):
    if zeit.cms.checkout.interfaces.ILocalContent.providedBy(context):
        context = zeit.cms.interfaces.ICMSContent(context.uniqueId)
    return context.__parent__


@grok.adapter(zeit.cms.repository.interfaces.IFolder)
@grok.implementer(zeit.content.image.browser.interfaces.IUploadTarget)
def folder_target(context):
    return context


@grok.adapter(zeit.cms.interfaces.ICMSContent)
@grok.implementer(zeit.content.image.browser.interfaces.IUploadBaseName)
def default_base_name(context):
    renameable = zeit.cms.repository.interfaces.IAutomaticallyRenameable(context)
    if renameable.renameable:
        # This is a new article, so don't use its (temporary) file name.
        # Instead, take the new target name as given by the user (if available).
        return renameable.rename_to
    return context.__name__


@grok.adapter(zeit.cms.repository.interfaces.IFolder)
@grok.implementer(zeit.content.image.browser.interfaces.IUploadBaseName)
def folder_base_name(context):
    return None


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

    @cachedproperty
    def folder(self):
        return zeit.content.image.browser.interfaces.IUploadTarget(self.context)

    def handle_cancel(self):
        for file in self._files:
            del self.folder[file['tmp_name']]
        self.redirect(self.url(name=''), status=303)

    def handle_submit(self):
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(self.folder)
        taken_names = set()
        for file in self._files:
            if (file['target_name'] != file['tmp_name'] and file['target_name'] in self.folder) or (
                file['target_name'] in taken_names
            ):
                self._errors[file['tmp_name']] = _('File name is already in use')
            taken_names.add(file['target_name'])

        if self._errors:
            return super().__call__()

        for file in self._files:
            tmp_name = file['tmp_name']
            name = file['target_name']
            # Since tmp_name ends with '.tmp', and target_name is normalized
            # (which replaces the '.' with '-'), the two always differ.
            renamer.renameItem(tmp_name, name)
            with zeit.cms.checkout.helper.checked_out(
                self.folder[name], temporary=False, raise_if_error=True
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

            if 'upload_and_publish' in self.request.form:
                IPublish(self.folder[name]).publish()

        return_url = zope.component.queryMultiAdapter(
            (self.context, self.request), zeit.content.image.browser.interfaces.IUploadReturnURL
        )

        if 'upload_and_open' in self.request.form:
            if len(self._files) > 1:
                image_urls = []
                for file in self._files:
                    image_url = self.url(self.folder[file['target_name']], '@@variant.html')
                    image_urls.append(image_url)
                return self._open_multiple_images(image_urls)
            else:
                url = self.url(
                    self.folder[self._files[0]['target_name']],
                    name='@@variant.html',
                )
        elif return_url is not None:
            url = return_url
        elif len(self._files) == 1:
            url = self.url(self.folder[self._files[0]['target_name']], name='@@variant.html')
        else:
            url = self.url(self.folder)

        self.redirect(url, status=303)

    def _parse_get_request(self):
        from_name = zeit.content.image.browser.interfaces.IUploadBaseName(self.context, None)

        filenames = self.request.form.get('files', ())
        if isinstance(filenames, str):
            filenames = (filenames,)

        name_provider = ImageNameProvider(self.folder)
        for tmp_name in filenames:
            imggroup = self.folder[tmp_name]

            meta = parse_fields_from_embedded_metadata(
                imggroup[imggroup.master_image].embedded_metadata_flattened()
            )

            name_base = None
            if from_name:
                name_base = from_name
            elif meta['title'] is not None:
                name_base = zeit.cms.interfaces.normalize_filename(meta['title'])
            else:
                filename = os.path.splitext(imggroup.master_image)[0]
                name_base = zeit.cms.interfaces.normalize_filename(filename)

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
                'thumbnail': self.url(self.folder[tmp_name], 'thumbnail'),
            }
            index += 1

    def rows(self):
        for file in self._files:
            res = dict(file)
            res['error'] = self._errors.get(file['tmp_name'], False)
            yield res

    def _open_multiple_images(self, urls):
        """Render a page that opens multiple image URLs with delays
        which avoid noisy zodb transaction errors,
        first image will reuse the current window,
        rest will open in new tabs"""
        self.request.response.setHeader('Content-Type', 'text/html')
        first_url = urls[0]
        remaining_urls_js = ', '.join(f'"{url}"' for url in urls[1:])

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bilder werden geöffnet...</title>
            <meta charset="utf-8">
        </head>
        <body>
            <p>Bitte Pop-ups zulassen, wenn keine neuen Tabs geöffnet werden.</p>
            <script>
                const remainingUrls = [{remaining_urls_js}];

                function openRemainingUrls(urls, index = 0) {{
                    if (index >= urls.length) {{
                        window.location.href = '{first_url}';
                        return;
                    }}

                    try {{
                        window.open(urls[index], '_blank');
                    }} catch(e) {{
                        console.log('Failed to open:', urls[index]);
                    }}

                    setTimeout(() => {{
                        openRemainingUrls(urls, index + 1);
                    }}, 100);
                }}

                openRemainingUrls(remainingUrls);
            </script>
        </body>
        </html>
        """


def parse_fields_from_embedded_metadata(metadata):
    """Get title, copyright, caption from embedded metadata"""
    key_mapping = {
        'title': ['xmp:xmpmeta:Headline', 'xmp:xmpmeta:title:text'],
        'caption': ['xmp:xmpmeta:description:text'],
        'copyright': ['xmp:xmpmeta:creator', 'xmp:xmpmeta:Credit'],
    }

    def first_value(keys):
        for key in keys:
            if value := metadata.get(key):
                return value
        return None

    result = {}
    for field, keys in key_mapping.items():
        if field == 'copyright':
            # Join all present copyright values
            values = [metadata.get(key) for key in keys if metadata.get(key)]
            result[field] = '/'.join(str(v) for v in values) if values else None
        else:
            result[field] = first_value(keys)

    return result
