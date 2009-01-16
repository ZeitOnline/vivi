# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import persistent
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.repository
import zeit.connector.resource
import zeit.content.image.interfaces
import zope.app.container.contained
import zope.component
import zope.interface
import zope.security.proxy


class ImageGroupBase(object):

    zope.interface.implements(zeit.content.image.interfaces.IImageGroup)

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageGroup,
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        ('master_image', ))


class ImageGroup(ImageGroupBase,
                 zeit.cms.repository.repository.Container):

    zope.interface.implements(
        zeit.content.image.interfaces.IRepositoryImageGroup)

    def __getitem__(self, key):
        item = super(ImageGroup, self).__getitem__(key)
        if key == self.master_image:
            zope.interface.alsoProvides(
                item, zeit.content.image.interfaces.IMasterImage)
        return item


@zope.interface.implementer(zeit.content.image.interfaces.IImageGroup)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def imageGroupFactory(context):
    ig = ImageGroup()
    ig.uniqueId = context.id
    return ig


@zope.interface.implementer(zeit.connector.interfaces.IResource)
@zope.component.adapter(zeit.content.image.interfaces.IImageGroup)
def imageGroupToResource(context):
    try:
        properties = zeit.connector.interfaces.IWebDAVReadProperties(
            context)
    except TypeError:
        properties = zeit.connector.resource.WebDAVProperties()
    return zeit.connector.resource.Resource(
        context.uniqueId, context.__name__, 'image-group',
        data=StringIO.StringIO(),
        contentType='httpd/unix-directory',
        properties=properties)


class LocalImageGroup(ImageGroupBase,
                      persistent.Persistent,
                      zope.app.container.contained.Contained):

    zope.interface.implements(zeit.content.image.interfaces.ILocalImageGroup)


@zope.component.adapter(zeit.content.image.interfaces.IImageGroup)
@zope.interface.implementer(zeit.content.image.interfaces.ILocalImageGroup)
def local_image_group_factory(context):
    lig = LocalImageGroup()
    lig.uniqueId = context.uniqueId
    lig.__name__ = context.__name__
    zeit.connector.interfaces.IWebDAVWriteProperties(lig).update(
        zeit.connector.interfaces.IWebDAVReadProperties(
            zope.security.proxy.removeSecurityProxy(context)))
    return lig


@zope.component.adapter(zeit.content.image.interfaces.IImageGroup)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    metadata = zeit.content.image.interfaces.IImageMetadata(context)
    image = zope.component.getAdapter(
        metadata,
        zeit.cms.content.interfaces.IXMLReference, name='image')
    image.set('base-id', context.uniqueId)

    type = None
    for sub_image_name in context:
        if '.' not in sub_image_name:
            continue
        base, ext = sub_image_name.rsplit('.', 1)
        if base.endswith('x140'):
            # This is deciding
            type = ext
            break
        if type is None:
            # Just remember the first type
            type = ext

    image.set('type', type)
    # The image reference can be seen like an element in a feed. Let the magic
    # update the xml node.
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(image)
    return image
