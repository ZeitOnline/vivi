from collections.abc import Iterable
import urllib.parse
import uuid

import zope.formlib.form
import zope.formlib.widgets

from zeit.cms.i18n import MessageFactory as _
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

        self._files = self._parse_get_request()
        return super().__call__()

    def handle_cancel(self):
        for file in self._files:
            del self.context[file['cur_name']]
        self.redirect(self.url(name=''), status=303)

    def handle_submit(self):
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(self.context)
        taken_names = set()
        for file in self._files:
            if (file['name'] != file['cur_name'] and file['name'] in self.context) or (
                file['name'] in taken_names
            ):
                self._errors[file['cur_name']] = _('File name is already in use')
            taken_names.add(file['name'])

        if self._errors:
            return super().__call__()

        for file in self._files:
            cur_name = file['cur_name']
            name = file['name']
            if name != cur_name:
                renamer.renameItem(cur_name, name)
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

        if len(self._files) == 1:
            url = self.url(self.context[self._files[0]['name']], name='@@variant.html')
        else:
            url = self.url(name='')
        self.redirect(url, status=303)

    def _parse_get_request(self):
        from_name = self.request.form.get('from', None)
        filenames = self.request.form.get('files', ())
        if isinstance(filenames, str):
            filenames = (filenames,)
        name_index = 1
        for name in filenames:
            imggroup = self.context[name]

            meta = imggroup[imggroup.master_image].getXMPMetadata()

            if not from_name and meta['title'] is not None:
                from_name = zeit.cms.interfaces.normalize_filename(meta['title'])

            if from_name:
                while True:
                    suffix = ''
                    if len(filenames) >= 10:
                        suffix = f'-{name_index:02}'
                    elif name_index > 1 or len(filenames) > 1:
                        suffix = f'-{name_index}'
                    name = f'{from_name}-bild{suffix}'
                    name_index += 1
                    if name not in self.context:
                        break
            else:
                name = ''

            yield {
                'cur_name': imggroup.__name__,
                'name': name,
                'title': meta['title'],
                'copyright': meta['copyright'],
                'caption': meta['caption'],
                'thumbnail': self.url(imggroup, 'thumbnail'),
            }

    def _parse_post_request(self):
        index = 0
        while f'cur_name[{index}]' in self.request.form:
            cur_name = self.request.form[f'cur_name[{index}]']
            name = self.request.form[f'name[{index}]']
            yield {
                'cur_name': cur_name,
                'name': name,
                'title': self.request.form[f'title[{index}]'],
                'copyright': self.request.form[f'copyright[{index}]'],
                'caption': self.request.form[f'caption[{index}]'],
                'thumbnail': self.url(self.context[cur_name], 'thumbnail'),
            }
            index += 1

    def rows(self):
        for file in self._files:
            res = dict(file)
            res['error'] = self._errors.get(file['cur_name'], False)
            yield res
