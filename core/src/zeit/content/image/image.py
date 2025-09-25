from contextlib import contextmanager
import io
import os
import urllib.parse

from PIL import ImageCms
import grokcore.component as grok
import lxml.builder
import lxml.etree
import opentelemetry.trace
import PIL.Image
import requests
import zope.cachedescriptors.property
import zope.component
import zope.event
import zope.interface
import zope.lifecycleevent
import zope.location.interfaces
import zope.security.proxy

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.content.image import embedded
import zeit.cms.checkout.interfaces
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


class BaseImage:
    def __init__(self, uniqueId=None):
        super().__init__(uniqueId)

    _mime_type = zeit.cms.content.dav.DAVProperty(
        zeit.content.image.interfaces.IImage['mime_type'],
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        'mime_type',
    )

    _width = zeit.cms.content.dav.DAVProperty(
        zeit.content.image.interfaces.IImage['width'],
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        'width',
    )

    _height = zeit.cms.content.dav.DAVProperty(
        zeit.content.image.interfaces.IImage['height'],
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        'height',
    )

    @contextmanager
    def as_pil(self, keep_metadata=False):
        with self.open() as f:
            pil = PIL.Image.open(f)
            pil.load()

        with pil as pil:
            if keep_metadata:
                pil.encoderinfo = pil.info.copy()
            yield pil

    def embedded_metadata(self):
        with self.as_pil() as img:
            return self._metadata(img)

    def embedded_metadata_flattened(self):
        with self.as_pil() as img:
            metadata = self._metadata(img)
            try:
                return self._flatten(metadata)
            except Exception as err:
                message = f'Unable to flatten image metadata for {self.uniqueId}: {err}'
                opentelemetry.trace.get_current_span().add_event(
                    'exception',
                    {
                        'exception.type': 'FlattenMetadataError',
                        'exception.severity': 'info',
                        'exception.message': message,
                    },
                )
                return {}

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
            if all([type(i) in [str, int, float] for i in data]):
                result[parent] = ', '.join([str(i) for i in data])
            else:
                for x in data:
                    result.update(self._flatten(x, parent))
        elif isinstance(data, str) and not data.strip():
            pass
        else:
            result[parent] = data

        return result

    def _metadata(self, img):
        metadata = img.info.copy() if isinstance(img.info, dict) else {}
        metadata['iptc'] = embedded.iptc(img)
        metadata['exif'] = embedded.exif(img)
        metadata['xmp'] = img.getxmp()
        if 'icc_profile' in metadata:
            icc_data = io.BytesIO(metadata['icc_profile'])
            profile = ImageCms.ImageCmsProfile(icc_data)
            metadata['icc_profile'] = embedded.icc(profile)
        return metadata

    @property
    def mimeType(self):
        if FEATURE_TOGGLES.find('column_read_wcm_56'):
            return self._mime_type
        return self._parse_mime()

    def _parse_mime(self):
        with self.as_pil() as pil:
            return PIL.Image.MIME.get(pil.format, '')

    @mimeType.setter
    def mimeType(self, value):
        self._mime_type = value

    @property
    def width(self):
        if FEATURE_TOGGLES.find('column_read_wcm_56'):
            return self._width
        return self._parse_size()[0]

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        if FEATURE_TOGGLES.find('column_read_wcm_56'):
            return self._height
        return self._parse_size()[1]

    @height.setter
    def height(self, value):
        self._height = value

    def getImageSize(self):
        if FEATURE_TOGGLES.find('column_read_wcm_56'):
            return (self.width, self.height)
        return self._parse_size()

    def _parse_size(self):
        with self.as_pil() as img:
            return img.size

    @property
    def ratio(self):
        try:
            # Spell more explicitly, to prevent calling _parse_size() twice
            if FEATURE_TOGGLES.find('column_read_wcm_56'):
                return float(self.width) / float(self.height)
            width, height = self._parse_size()
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
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(image))
    return image


@grok.subscribe(zeit.content.image.interfaces.IImage, zope.lifecycleevent.IObjectCreatedEvent)
def set_image_properties(context, event):
    if FEATURE_TOGGLES.find('column_write_wcm_56'):
        with context.as_pil() as pil:
            context.mimeType = PIL.Image.MIME.get(pil.format, '')
            (context.width, context.height) = pil.size


@grok.subscribe(
    zeit.content.image.interfaces.IImage, zeit.cms.checkout.interfaces.IBeforeCheckinEvent
)
def update_image_properties(context, event):
    return set_image_properties(context, event)
