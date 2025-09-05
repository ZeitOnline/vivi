from contextlib import contextmanager
import os
import urllib.parse

import filetype
import lxml.builder
import lxml.etree
import PIL.Image
import requests
import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.location.interfaces
import zope.security.proxy

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
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


# Kludgy way to make Pillow use lxml for XMP parsing.
# Cannot use monkey:patch for unknown reason.
PIL.Image.ElementTree = lxml.etree


def extract_metadata_from_xmp(xmp):
    result = {'title': None, 'copyright': None, 'caption': None}
    if 'xapmeta' in xmp:
        data = xmp['xapmeta']
        data = data.get('RDF', {}).get('Description', {})
        if isinstance(data, dict):
            data = (data,)
        for item in data:
            if 'Headline' in item:
                result['title'] = item['Headline']
            if 'creator' in item:
                result['creator'] = item['creator'].get('Seq', {}).get('li', None)
            if 'Credit' in item:
                result['credit'] = item['Credit']
            if 'description' in item:
                result['caption'] = (
                    item.get('description', {}).get('Alt', {}).get('li', {}).get('text', None)
                )
    if 'xmpmeta' in xmp:
        data = xmp['xmpmeta']
        data = data.get('RDF', {}).get('Description', {})
        if isinstance(data, dict):
            data = (data,)
        for item in data:
            if 'Headline' in item:
                result['title'] = item['Headline']
            if 'creator' in item:
                result['creator'] = item['creator'].get('Seq', {}).get('li', None)
            if 'Credit' in item:
                result['credit'] = item['Credit']
            if 'description' in item:
                result['caption'] = (
                    item.get('description', {}).get('Alt', {}).get('li', {}).get('text', None)
                )

    if 'credit' in result or 'creator' in result:
        result['copyright'] = '/'.join(
            filter(None, (result.get('creator', None), result.get('credit', None)))
        )
        if 'credit' in result:
            del result['credit']
        if 'creator' in result:
            del result['creator']
    return result


class BaseImage:
    def __init__(self, uniqueId=None):
        super().__init__(uniqueId)

    _mime_type = zeit.cms.content.dav.DAVProperty(
        zeit.content.image.interfaces.IImage['mime_type'],
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        'mime_type',
    )

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImage,
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        ('width', 'height'),
    )

    @contextmanager
    def as_pil(self):
        with self.open() as f:
            with PIL.Image.open(f) as pil:
                yield pil

    @property
    def mimeType(self):
        if FEATURE_TOGGLES.find('column_read_wcm_56'):
            return self._mime_type
        return self.getMimeType()

    @mimeType.setter
    def mimeType(self, value):
        self._mime_type = value

    def getMimeType(self):
        with self.open() as f:
            head = f.read(261)
        file_type = filetype.guess_mime(head) or ''
        if not file_type.startswith('image/'):
            return ''
        return file_type

    def getImageSize(self):
        with self.as_pil() as img:
            return img.size

    def getXMPMetadata(self):
        with self.as_pil() as img:
            return extract_metadata_from_xmp(img.getxmp())

    @property
    def ratio(self):
        try:
            if FEATURE_TOGGLES.find('column_read_wcm_56'):
                return float(self.width) / float(self.height)
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
    zeit.content.image.interfaces.IImage, zope.location.interfaces.IContained
)
class RepositoryImage(BaseImage, zeit.cms.repository.file.RepositoryFile):
    pass


@zope.interface.implementer_only(
    zeit.content.image.interfaces.IImage,
    zeit.cms.workingcopy.interfaces.ILocalContent,
    zope.location.interfaces.IContained,
)
class LocalImage(BaseImage, zeit.cms.repository.file.LocalFile):
    pass


class TemporaryImage(LocalImage):
    def open(self, mode='r'):
        if mode not in ('r', 'w'):
            raise ValueError(mode)

        if self.local_data is None:
            if mode == 'r':
                raise ValueError('Cannot open for reading, no data available.')
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
        zeit.cms.interfaces.IWebDAVProperties(context)
    )
    # Hrmpf. I don't quite like this:
    if zeit.content.image.interfaces.IMasterImage.providedBy(context):
        zope.interface.alsoProvides(local, zeit.content.image.interfaces.IMasterImage)
    return local


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    image = lxml.builder.E.image()
    image.set('src', context.uniqueId)
    if '.' in context.__name__:
        base, ext = context.__name__.rsplit('.', 1)
        image.set('type', ext)
    else:
        image.set('type', context.format.lower())
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


KiB = 1024
DOWNLOAD_CHUNK_SIZE = 2 * KiB


def get_remote_image(url, timeout=2):
    try:
        response = requests.get(url, stream=True, timeout=timeout)
    except Exception:
        return None
    if not response.ok:
        response.close()
        return None
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
