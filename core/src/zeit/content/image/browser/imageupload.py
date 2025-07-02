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


class UploadForm(zeit.cms.browser.view.Base):
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

        form = zeit.content.image.browser.imagegroup.AddForm(None, None)
        form.new_object = imagegroup
        form.adapters = {}
        imagegroup = form.create({'master_image_blobs': (file,)})

        name = f'{uuid.uuid4()}.tmp'
        zeit.cms.repository.interfaces.IAutomaticallyRenameable(imagegroup).renameable = True
        parent[name] = imagegroup

        for image in form.images:
            if image is not None:
                imagegroup[image.__name__] = image
        return name


class EditForm(zeit.cms.browser.view.Base):
    # FIXME: Translations
    title = _('Edit images')

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
                    'description': data.get('description', {})
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
