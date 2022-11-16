from zeit.cms.i18n import MessageFactory as _
import PIL.Image
import lxml.objectify
import magic
import os
import requests
import urllib.parse
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.file
import zeit.cms.type
import zeit.cms.util
import zeit.cms.workingcopy.interfaces
import zeit.content.image.imagegroup
import zeit.content.image.interfaces
import zeit.workflow.interfaces
import zeit.workflow.timebased
import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.location.interfaces
import zope.security.proxy


class FakeWriteableCachedProperty(zope.cachedescriptors.property.Lazy):

    def __get__(self, inst, class_):
        if inst is None:
            return self

        func, name = self.data
        # Because we define __set__, we take precedence over the instance dict
        if name in inst.__dict__:
            return inst.__dict__[name]

        value = func(inst)
        inst.__dict__[name] = value
        return value

    def __set__(self, inst, value):
        pass


class BaseImage:

    def __init__(self, uniqueId=None):
        super().__init__(uniqueId, mimeType='')

    # Not writeable since we always calculate it, but our superclasses want to.
    @FakeWriteableCachedProperty
    def mimeType(self):
        with self.open() as f:
            head = f.read(200)
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            file_type = m.id_buffer(head)
        if not file_type.startswith('image/'):
            return ''
        return file_type

    def getImageSize(self):
        with self.open() as f:
            return PIL.Image.open(f).size

    @property
    def ratio(self):
        try:
            width, height = self.getImageSize()
            return float(width) / float(height)
        except Exception:
            return None

    FORMATS = {
        'jpg': 'JPEG',
        'x-ms-bmp': 'BMP',
    }

    @property
    def format(self):
        subtype = self.mimeType.split('/')[-1]
        return self.FORMATS.get(subtype, subtype.upper())


@zope.interface.implementer_only(
    zeit.content.image.interfaces.IImage,
    zope.location.interfaces.IContained)
class RepositoryImage(BaseImage, zeit.cms.repository.file.RepositoryFile):
    pass


@zope.interface.implementer_only(
    zeit.content.image.interfaces.IImage,
    zeit.cms.workingcopy.interfaces.ILocalContent,
    zope.location.interfaces.IContained)
class LocalImage(BaseImage, zeit.cms.repository.file.LocalFile):
    pass


class TemporaryImage(LocalImage):

    def open(self, mode='r'):
        if mode not in ('r', 'w'):
            raise ValueError(mode)

        if self.local_data is None:
            if mode == 'r':
                raise ValueError("Cannot open for reading, no data available.")
            if mode == 'w':
                self.local_data = zeit.cms.util.MemoryFile()
        else:
            self.local_data.close()

        return self.local_data


@zope.component.adapter(RepositoryImage)
@zope.interface.implementer(zeit.cms.workingcopy.interfaces.ILocalContent)
def localimage_factory(context):
    local = LocalImage(context.uniqueId)
    local.__name__ = context.__name__
    zeit.cms.interfaces.IWebDAVProperties(local).update(
        zeit.cms.interfaces.IWebDAVProperties(context))
    # Hrmpf. I don't quite like this:
    if zeit.content.image.interfaces.IMasterImage.providedBy(context):
        zope.interface.alsoProvides(
            local, zeit.content.image.interfaces.IMasterImage)
    return local


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    image = lxml.objectify.E.image()
    image.set('src', context.uniqueId)
    if '.' in context.__name__:
        base, ext = context.__name__.rsplit('.', 1)
        image.set('type', ext)
    else:
        image.set('type', context.format.lower())
    # The image reference can be seen like an element in a feed. Let the magic
    # update the xml node.
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(image)
    return image


class ImageType(zeit.cms.type.TypeDeclaration):

    interface = zeit.content.image.interfaces.IImage
    interface_type = zeit.content.image.interfaces.IImageType
    type = 'image'
    title = _('Image')
    factory = RepositoryImage

    def content(self, resource):
        return self.factory(resource.id)

    def resource_body(self, content):
        return zope.security.proxy.removeSecurityProxy(content.open('r'))

    def resource_content_type(self, content):
        return content.mimeType


@zope.component.adapter(zeit.content.image.interfaces.IImage)
class XMLReferenceUpdater(zeit.workflow.timebased.XMLReferenceUpdater):

    target_iface = zeit.workflow.interfaces.ITimeBasedPublishing

    def update_with_context(self, entry, workflow):
        super().update_with_context(entry, workflow)

        parent = zope.security.proxy.removeSecurityProxy(
            workflow).context.__parent__
        if not zeit.content.image.interfaces.IImageGroup.providedBy(parent):
            return

        if not entry.get('expires'):
            parent_workflow = self.target_iface(parent)
            super().update_with_context(
                entry, parent_workflow)


KiB = 1024
DOWNLOAD_CHUNK_SIZE = 2 * KiB


def get_remote_image(url, timeout=2):
    try:
        response = requests.get(url, stream=True, timeout=timeout)
    except Exception:
        return
    if not response.ok:
        response.close()
        return
    image = LocalImage()
    image.__name__ = os.path.basename(urllib.parse.urlsplit(url).path)
    with image.open('w') as fh:
        first_chunk = True
        for chunk in response.iter_content(DOWNLOAD_CHUNK_SIZE):
            # Too small means something is not right with this download
            if first_chunk:
                first_chunk = False
                assert len(chunk) > DOWNLOAD_CHUNK_SIZE / 2
            fh.write(chunk)
    return image
