# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import PIL.Image
import urlparse
import z3c.conditionalviews
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.view
import zeit.cms.content.property
import zeit.cms.repository.interfaces
import zeit.cms.settings.interfaces
import zeit.connector.interfaces
import zeit.content.image.imagereference
import zeit.content.image.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.file.download
import zope.publisher.interfaces


def get_img_tag(image, request):
    """Render <img.../>-tag."""
    url = zope.component.getMultiAdapter(
        (image, request), name='absolute_url')
    width, height = image.getImageSize()
    return (
        '<img src="%s" alt="" height="%s" width="%s" border="0" />' % (
        url, height, width))


class Image(zope.file.download.Display):

    def __call__(self):
        self.request.response.setHeader('Content-Type', self.context.mimeType)
        return self.stream_image()

    @z3c.conditionalviews.ConditionalView
    def stream_image(self):
        return super(Image, self).__call__()


class ImageView(zeit.cms.browser.view.Base):

    title = _('View image')

    @zope.cachedescriptors.property.Lazy
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)

    def tag(self):
        return get_img_tag(self.context, self.request)

    @property
    def width(self):
        return self.context.getImageSize()[0]

    @property
    def height(self):
        return self.context.getImageSize()[1]

    @property
    def copyrights(self):
        result = []
        for copyright, url in self.metadata.copyrights:
            result.append(dict(
                copyright=copyright,
                url=url))
        return result


class Scaled(object):

    filter = PIL.Image.ANTIALIAS

    def __call__(self):
        return self.scaled()

    def tag(self):
        return get_img_tag(self.scaled.context, self.request)

    @zope.cachedescriptors.property.Lazy
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


class ImageListRepresentation(
    zeit.cms.browser.listing.BaseListRepresentation):
    """Adapter for listing article content resources"""

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.content.image.interfaces.IImage,
                          zope.publisher.interfaces.IPublicationRequest)

    author = ressort = page = u''

    @property
    def title(self):
        title = self.image_metadata.title
        if not title:
            title = self.context.__name__
        return title

    @property
    def volume(self):
        return self.image_metadata.volume

    @property
    def year(self):
        return self.image_metadata.year

    @property
    def searchableText(self):
        # XXX
        return ''

    @zope.cachedescriptors.property.Lazy
    def image_metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)


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


class MetadataPreviewHTML(object):

    @zope.cachedescriptors.property.Lazy
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)
