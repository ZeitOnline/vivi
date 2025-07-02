from collections.abc import Iterable
import urllib.parse
import uuid

import lxml.etree
import PIL.Image
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


class UploadForm(zeit.cms.browser.view.Base, zeit.content.image.browser.form.CreateImageMixin):
    # FIXME: Translations
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

        files = self.request.form['files']
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


class EditForm(zeit.cms.browser.view.Base):
    # FIXME: Translations
    title = _('Edit images')

    def __call__(self):
        if self.request.method == 'POST':
            return self.handle_post()
        return super().__call__()

    def handle_post(self):
        index = 0
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(self.context)
        while f'cur_name[{index}]' in self.request.form:
            cur_name = self.request.form[f'cur_name[{index}]']
            name = self.request.form[f'name[{index}]']
            renamer.renameItem(cur_name, name)
            with zeit.cms.checkout.helper.checked_out(self.context[name]) as imagegroup:
                if imagegroup is not None:
                    metadata = zeit.content.image.interfaces.IImageMetadata(imagegroup)
                    metadata.copyright = (
                        None,
                        None,
                        self.request.form[f'copyright[{index}]'],
                        None,
                        False,
                    )
                    metadata.title = self.request.form[f'title[{index}]']
                    metadata.caption = self.request.form[f'caption[{index}]']
            index += 1
        self.redirect(self.url(name=''), status=303)

    def rows(self):
        from_name = self.request.form.get('from', None)
        filenames = self.request.form.get('files', ())
        if isinstance(filenames, str):
            filenames = (filenames,)
        result = []
        name_index = 1
        for name in filenames:
            imggroup = self.context[name]

            if from_name:
                while True:
                    suffix = ''
                    if len(filenames) >= 10:
                        suffix = f'-{name_index:02}'
                    elif name_index > 1 or len(filenames) > 1:
                        suffix = f'-{name_index}'
                    name = f'{from_name}-bild{suffix}'
                    name_index += 1
                    if not self.context.get(name):
                        break

            data = self._image_data(imggroup[imggroup.master_image])
            data = data.get('xmpmeta', {}).get('RDF', {}).get('Description', {})
            result.append(
                {
                    'cur_name': imggroup.__name__,
                    'name': name,
                    'title': data.get('Headline', ''),
                    'copyright': ' / '.join(
                        filter(
                            None,
                            (
                                data.get('creator', {}).get('Seq', {}).get('li', None),
                                data.get('Credit', None),
                            ),
                        )
                    ),
                    'caption': data.get('description', {})
                    .get('Alt', {})
                    .get('li', {})
                    .get('text', ''),
                    'thumbnail': self.url(imggroup, 'thumbnail'),
                }
            )
        return result

    def _image_data(self, img):
        try:
            with zope.security.proxy.removeSecurityProxy(img.open()) as f:
                PIL.Image.ElementTree = lxml.etree
                image = PIL.Image.open(f)
                image.load()
                return image.getxmp()
        except IOError:
            # FIXME: only log
            raise zeit.content.image.interfaces.ImageProcessingError(
                'Cannot retrieve XMP metadata from image %s' % img.__name__
            )
