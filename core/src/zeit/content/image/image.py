from contextlib import contextmanager
import os
import urllib.parse

from PIL import IptcImagePlugin
from PIL.ExifTags import TAGS
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

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.file
import zeit.cms.type
import zeit.cms.util
import zeit.cms.workingcopy.interfaces
import zeit.content.image.imagegroup
import zeit.content.image.interfaces
import zeit.content.image.xmp
import zeit.workflow.interfaces
import zeit.workflow.timebased


class BaseImage:
    def __init__(self, uniqueId=None):
        super().__init__(uniqueId)

    @contextmanager
    def as_pil(self, keep_metadata=False):
        with self.open() as f:
            pil = PIL.Image.open(f)
            pil.load()
        with pil as pil:
            if keep_metadata:
                pil.encoderinfo = pil.info.copy()
            yield pil

    @property
    def mimeType(self):
        with self.open() as f:
            head = f.read(261)
        file_type = filetype.guess_mime(head) or ''
        if not file_type.startswith('image/'):
            return ''
        return file_type

    def _flatten(self, data, parent=''):
        """Kludgy heuristics to try to flatten the nested XMP/RDF structure into
        a single key-value dict."""
        result = {}

        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['about', 'lang']:
                    continue
                if key in ['RDF', 'Description', 'Seq', 'Bag', 'Alt', 'li']:
                    key = parent
                else:
                    key = f'{parent}:{key}' if parent else key
                result.update(self._flatten(value, key))
        elif isinstance(data, list):
            if isinstance(data[0], str):
                result[parent] = ', '.join(data)
            else:
                for x in data:
                    result.update(self._flatten(x, parent))
        elif isinstance(data, str) and not data.strip():
            pass
        else:
            result[parent] = data

        return result

    @staticmethod
    def _metadata(img):
        """See https://de.wikipedia.org/wiki/IPTC-IIM-Standard for a list of available iptc tags"""
        metadata = img.info.copy() if isinstance(img.info, dict) else {}
        iptc_tags = {(2, 110): 'copyright', (2, 120): 'caption', (2, 105): 'title'}
        iptc = IptcImagePlugin.getiptcinfo(img)
        if isinstance(iptc, dict):
            metadata['iptc'] = {}
            for code, value in iptc.items():
                tag_name = iptc_tags.get(code, code)
                metadata['iptc'][tag_name] = value
        metadata['exif'] = {}
        for tag_id, value in img.getexif().items():
            tag_name = TAGS.get(tag_id, tag_id)
            metadata['exif'][tag_name] = value
        metadata['xmp'] = img.getxmp()
        return metadata

    def getImageSize(self):
        with self.as_pil() as img:
            return img.size

    def getXMPMetadata(self):
        with self.as_pil() as img:
            return zeit.content.image.xmp.extract_metadata(img.getxmp())

    def embedded_metadata_flattened(self):
        with self.as_pil() as img:
            return self._flatten(self._metadata(img))

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
