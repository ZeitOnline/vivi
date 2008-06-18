# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urlparse

import zope.cachedescriptors.property
import zope.component
import zope.publisher.interfaces

import zope.app.file.browser.image

import zeit.cms.content.property
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.repository.interfaces
import zeit.content.image.interfaces
from zeit.cms.i18n import MessageFactory as _


class Image(zope.app.file.browser.image.ImageData):

    def __call__(self):
        return self.show()

    @property
    def width(self):
        return self.context.getImageSize()[0]

    @property
    def height(self):
        return self.context.getImageSize()[1]


class ImageView(object):

    title = _('View image')

    @zope.cachedescriptors.property.Lazy
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)


class Scaled(object):

    def __call__(self):
        return self.scaled()

    def tag(self, *args, **kwargs):
        return self.scaled.tag(*args, **kwargs)

    @zope.cachedescriptors.property.Lazy
    def scaled(self):
        try:
            image = zeit.content.image.interfaces.ITransform(self.context)
        except TypeError:
            image = self.context
        else:
            image = image.thumbnail(self.width, self.height)
            image.__name__ = self.__name__
        image_view = zope.component.getMultiAdapter(
            (image, self.request), name='index.html')
        return image_view

    @property
    def width(self):
        return self.scaled.getImageSize()[0]

    @property
    def height(self):
        return self.scaled.getImageSize()[1]


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

    split = list(urlparse.urlsplit(unique_id))
    path = split[2]

    path = path.replace('/online', '', 1)
    if not path.startswith('/bilder'):
        path = '/bilder' + path

    split[2] = path
    unique_id = urlparse.urlunsplit(split)

    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    try:
        image_folder = repository.getContent(unique_id)
    except KeyError:
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
        (context.context, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)


class MetadataPreviewHTML(object):

    @zope.cachedescriptors.property.Lazy
    def metadata(self):
        return zeit.content.image.interfaces.IImageMetadata(self.context)
