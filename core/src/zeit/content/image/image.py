# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL.Image

import gocept.lxml.interfaces
import zope.app.container.contained
import zope.app.container.interfaces
import zope.app.file.image
import zope.component
import zope.interface
import zope.security.proxy

import zeit.cms.connector
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.util
import zeit.cms.interfaces
import zeit.cms.repository.file
import zeit.cms.workingcopy.interfaces
import zeit.content.image.interfaces


class Image(zope.app.file.image.Image,
            zope.app.container.contained.Contained):
    """Image contanis exactly one image."""

    zope.interface.implements(zeit.content.image.interfaces.IImage)
    uniqueId = None

    # XXX keep image class for migration


class BaseImage(object):

    def getImageSize(self):
        return PIL.Image.open(self.open()).size


class RepositoryImage(BaseImage,
                      zeit.cms.repository.file.RepositoryFile):

    zope.interface.implementsOnly(
        zeit.content.image.interfaces.IImage,
        zope.app.container.interfaces.IContained)


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def repositoryimage_factory(context):
    try:
        pil_image = PIL.Image.open(context.data)
    except IOError:
        return None
    content_type = context.contentType
    if not content_type:
        content_type = 'image/' + pil_image.format.lower()
    return RepositoryImage(context.id, content_type)


class LocalImage(BaseImage,
                 zeit.cms.repository.file.LocalFile):

    zope.interface.implementsOnly(
        zeit.content.image.interfaces.IImage,
        zeit.cms.workingcopy.interfaces.ILocalContent,
        zope.app.container.interfaces.IContained)


@zope.component.adapter(RepositoryImage)
@zope.interface.implementer(zeit.cms.workingcopy.interfaces.ILocalContent)
def localimage_factory(context):
    local= LocalImage(context.uniqueId, context.mimeType)
    local.__name__ = context.__name__
    zeit.cms.interfaces.IWebDAVProperties(local).update(
        zeit.cms.interfaces.IWebDAVProperties(context))
    # Hrmpf. I don't quite like this:
    if zeit.content.image.interfaces.IMasterImage.providedBy(context):
        zope.interface.alsoProvides(
            local, zeit.content.image.interfaces.IMasterImage)
    return local


@zope.interface.implementer(zeit.cms.interfaces.IResource)
@zope.component.adapter(zeit.content.image.interfaces.IImage)
def resource_factory(context):
    return zeit.cms.connector.Resource(
        context.uniqueId, context.__name__, 'image',
        zope.security.proxy.removeSecurityProxy(context.open('r')),
        contentType=context.mimeType,
        properties=zeit.cms.interfaces.IWebDAVProperties(context))


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    metadata = zeit.content.image.interfaces.IImageMetadata(context)
    image = zope.component.getAdapter(
        metadata,
        zeit.cms.content.interfaces.IXMLReference, name='image')
    image.set('src', context.uniqueId)
    if '.' in context.__name__:
        base, ext = context.__name__.rsplit('.', 1)
        image.set('type', ext)
    # The image reference can be seen like an element in a feed. Let the magic
    # update the xml node.
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(image)
    return image
