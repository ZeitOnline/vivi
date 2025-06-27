from collections.abc import Iterable
import urllib.parse
import uuid

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.view
import zeit.cms.browser.widget
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

    def handle_post(self):
        # Since self.context is potentially checked out, we cannot rely on self.context.__parent__
        target = zeit.cms.interfaces.ICMSContent(self.context.uniqueId)

        # If we upload in a folder, we don't want to go up
        if not zeit.cms.repository.interfaces.IFolder.providedBy(target):
            target = target.__parent__

        files = self.request.form['files']
        if not isinstance(files, Iterable):
            files = (files,)

        results = []
        for file in files:
            result = self._upload_imagegroup(file, target)
            results.append(result)

        url = (
            self.url(target, '@@edit-images')
            + '?'
            + urllib.parse.urlencode((('files', results),), doseq=True)
        )
        self.redirect(url, status=303)

    def _upload_imagegroup(self, file, parent):
        imagegroup = zeit.content.image.imagegroup.ImageGroup()

        form = zeit.content.image.browser.imagegroup.AddForm(None, None)
        form.new_object = imagegroup
        form.adapters = {}
        imagegroup = form.create({'master_image_blobs': (file,)})

        name = '{0}.tmp'.format(uuid.uuid4())
        zeit.cms.repository.interfaces.IAutomaticallyRenameable(imagegroup).renameable = True
        parent[name] = imagegroup

        for image in form.images:
            if image is not None:
                imagegroup[image.__name__] = image
        return name


class EditForm(zeit.cms.browser.view.Base):
    pass
