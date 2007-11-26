# Copyright (c) 2007 gocept gmbh & co. kg
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


class Image(zope.app.file.browser.image.ImageData):

    @property
    def width(self):
        return self.context.getImageSize()[0]

    @property
    def height(self):
        return self.context.getImageSize()[1]


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
            (image, self.request),
            name='index.html')
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
    zeit.cms.content.property.mapAttributes('volume', 'year')

    @property
    def title(self):
        title = self.context.title
        if not title:
            title = self.context.__name__
        return title

    @property
    def searchableText(self):
        # XXX
        return ''



@zope.component.adapter(
    zeit.cms.repository.interfaces.IFolder,
    zeit.content.image.interfaces.IImageType)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def imagefolder_browse_location(context, schema):
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
        image_folder = zope.component.queryMultiAdapter(
            (context, zeit.cms.interfaces.ICMSContent),
            zeit.cms.browser.interfaces.IDefaultBrowsingLocation)

    return image_folder
