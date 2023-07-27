from zeit.cms.i18n import MessageFactory as _
from zeit.content.image.interfaces import INFOGRAPHIC_DISPLAY_TYPE
from zope.browserpage import ViewPageTemplateFile
from zope.cachedescriptors.property import Lazy as cachedproperty
import PIL.Image
import importlib.resources
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.view
import zeit.cms.repository.interfaces
import zeit.cms.settings.interfaces
import zeit.connector.interfaces
import zeit.content.image.imagereference
import zeit.content.image.interfaces
import zope.component
import zope.file.download
import zope.publisher.interfaces


def get_img_tag(image, request, view=None):
    """Render <img.../>-tag."""
    url = zope.component.getMultiAdapter(
        (image, request), name='absolute_url')
    width, height = image.getImageSize()
    if view:
        view = '/' + view
    else:
        view = ''
    return (
        '<img src="%s%s" alt="" height="%s" width="%s" border="0" />' % (
            url, view, height, width))


class Image(zope.file.download.Display):

    def __call__(self):
        self.request.response.setHeader('Content-Type', self.context.mimeType)
        return self.stream_image()

    def stream_image(self):
        return super().__call__()


class ImageView(zeit.cms.browser.view.Base):

    title = _('View image')

    @cachedproperty
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)

    def tag(self):
        return get_img_tag(self.context, self.request, view='@@raw')

    @property
    def width(self):
        return self.context.getImageSize()[0]

    @property
    def height(self):
        return self.context.getImageSize()[1]

    @property
    def copyright(self):
        if not self.metadata.copyright:
            return
        copyright, company, company_text, url, nofollow = (
            self.metadata.copyright)
        return dict(
            copyright=copyright,
            company=company,
            company_text=company_text,
            url=url,
            nofollow=nofollow)


class ReferenceDetailsHeading(zeit.cms.browser.objectdetails.Details):

    template = ViewPageTemplateFile(str((importlib.resources.files(
        'zeit.cms.browser') / 'object-details-heading.pt')))

    def __init__(self, context, request):
        super().__init__(context.target, request)

    def __call__(self):
        return self.template()


class ReferenceDetailsBody(ImageView):

    @cachedproperty
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(
            self.context.target)

    @cachedproperty
    def is_infographic(self):
        if zeit.content.image.interfaces.IImageGroup.providedBy(
                self.context.target):
            return self.context.target.display_type == INFOGRAPHIC_DISPLAY_TYPE
        return False

    def tag(self):
        return get_img_tag(self.context.target, self.request, view='@@raw')


class Scaled:

    filter = PIL.Image.Resampling.LANCZOS

    def __call__(self):
        return self.scaled()

    def tag(self):
        return get_img_tag(self.scaled.context, self.request)

    @cachedproperty
    def scaled(self):
        try:
            image = zeit.content.image.interfaces.ITransform(self.context)
        except TypeError:
            image = self.context
        else:
            image = image.thumbnail(self.width, self.height, self.filter)
            image.__name__ = self.__name__
        image_view = zope.component.getMultiAdapter(
            (image, self.request), name='raw')
        return image_view


class Preview(Scaled):

    width = 500
    height = 500


class MetadataPreview(Scaled):

    width = 500
    height = 90


class Thumbnail(Scaled):

    width = height = 100


@zope.component.adapter(
    zeit.content.image.interfaces.IImage,
    zope.publisher.interfaces.IPublicationRequest)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class ImageListRepresentation(
        zeit.cms.browser.listing.BaseListRepresentation):
    """Adapter for listing article content resources"""

    author = ressort = page = ''

    @property
    def title(self):
        try:
            title = zeit.content.image.interfaces.IImageMetadata(
                self.context).title
        except Exception:
            title = None
        if not title:
            title = self.context.__name__
        return title

    @property
    def volume(self):
        return None

    @property
    def year(self):
        return None

    @property
    def searchableText(self):
        # XXX
        return ''


@zope.component.adapter(
    zeit.cms.repository.interfaces.IFolder,
    zeit.content.image.interfaces.IImageSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def imagefolder_browse_location(context, source):
    """The image browse location is deduced from the current folder, i.e.

        for /online/2007/32 it is /bilder/2007/32

    """
    unique_id = context.uniqueId
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    base = image_folder = None
    try:
        obj_in_repository = repository.getContent(unique_id)
    except KeyError:
        pass
    else:
        # Try to get a base folder
        while base is None:
            properties = zeit.connector.interfaces.IWebDAVProperties(
                obj_in_repository, None)
            if properties is None:
                break
            base = properties.get(('base-folder',
                                   'http://namespaces.zeit.de/CMS/Image'))
            obj_in_repository = obj_in_repository.__parent__

    if base is not None:
        try:
            base_obj = repository.getContent(base)
        except KeyError:
            pass
        else:
            # Get from the base folder to the year/volume folder
            settings = zeit.cms.settings.interfaces.IGlobalSettings(context)
            try:
                image_folder = base_obj[
                    '%04d' % settings.default_year][
                    '%02d' % settings.default_volume]
            except KeyError:
                pass

    if image_folder is None:
        all_content_source = zope.component.getUtility(
            zeit.cms.content.interfaces.ICMSContentSource, name='all-types')
        image_folder = zope.component.queryMultiAdapter(
            (context, all_content_source),
            zeit.cms.browser.interfaces.IDefaultBrowsingLocation)

    return image_folder


@zope.component.adapter(
    zeit.content.image.imagereference.ImagesAdapter,
    zeit.content.image.interfaces.IImageSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def imageadapter_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.__parent__, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)


class MetadataPreviewHTML:

    @cachedproperty
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)
