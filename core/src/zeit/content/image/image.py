# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import PIL.Image
import zeit.cms.connector
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.util
import zeit.cms.interfaces
import zeit.cms.repository.file
import zeit.cms.type
import zeit.cms.workingcopy.interfaces
import zeit.content.image.interfaces
import zeit.workflow.interfaces
import zeit.workflow.timebased
import zope.app.container.contained
import zope.app.container.interfaces
import zope.app.file.image
import zope.component
import zope.interface
import zope.security.proxy


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


class ImageType(zeit.cms.type.TypeDeclaration):

    interface = zeit.content.image.interfaces.IImage
    interface_type = zeit.content.image.interfaces.IImageType
    type = 'image'
    title = _('Image')

    def content(self, resource):
        try:
            pil_image = PIL.Image.open(resource.data)
        except IOError:
            return None
        content_type = resource.contentType
        if not content_type:
            content_type = 'image/' + pil_image.format.lower()
        return RepositoryImage(resource.id, content_type)

    def resource_body(self, content):
        return zope.security.proxy.removeSecurityProxy(content.open('r'))

    def resource_content_type(self, content):
        return content.mimeType


class XMLReferenceUpdater(zeit.workflow.timebased.XMLReferenceUpdater):

    target_iface = zeit.workflow.interfaces.ITimeBasedPublishing
    zope.component.adapts(zeit.content.image.interfaces.IImage)

    def update_with_context(self, entry, workflow):
        super(XMLReferenceUpdater, self).update_with_context(entry, workflow)

        parent = zope.security.proxy.removeSecurityProxy(
            workflow).context.__parent__
        if not zeit.content.image.interfaces.IImageGroup.providedBy(parent):
            return

        if not entry.get('expires'):
            parent_workflow = self.target_iface(parent)
            super(XMLReferenceUpdater, self).update_with_context(
                entry, parent_workflow)
