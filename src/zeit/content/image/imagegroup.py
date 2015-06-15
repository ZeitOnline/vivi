from zeit.cms.i18n import MessageFactory as _
import StringIO
import grokcore.component as grok
import lxml.objectify
import persistent
import urlparse
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.repository
import zeit.cms.type
import zeit.content.image.interfaces
import zope.app.container.contained
import zope.interface
import zope.location.interfaces
import zope.security.proxy


class ImageGroupBase(object):

    zope.interface.implements(zeit.content.image.interfaces.IImageGroup)

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageGroup,
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        ('master_image',))

    _variants = zeit.cms.content.dav.DAVProperty(
        zeit.content.image.interfaces.IImageGroup['variants'],
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        'variants')

    @property
    def variants(self):
        if self._variants is None:
            return {}
        return self._variants

    @variants.setter
    def variants(self, value):
        self._variants = value

    def create_variant_image(self, key):
        variant = zeit.content.image.interfaces.IVariants(self).get(key)
        if variant is None:
            raise KeyError(key)
        master = zeit.content.image.interfaces.IMasterImage(self, None)
        if master is None:
            raise KeyError(key)
        repository = zeit.content.image.interfaces.IRepositoryImageGroup(self)
        if variant.name in repository:
            return repository[variant.name]
        image = zeit.content.image.interfaces.ITransform(master).crop(variant)
        image.__name__ = key
        image.__parent__ = self
        return image

    def variant_url(self, name, width, height):
        path = urlparse.urlparse(self.uniqueId).path
        if path.endswith('/'):
            path = path[:-1]
        return '{path}/{name}__{width}x{height}'.format(
            path=path,
            name=name, width=width, height=height)


class ImageGroup(ImageGroupBase,
                 zeit.cms.repository.repository.Container):

    zope.interface.implements(
        zeit.content.image.interfaces.IRepositoryImageGroup)

    def __getitem__(self, key):
        """The following URLs may render images:

        Image is present on disk:
        * /imagegroup/imagegroup-540x304.jpg
        * /imagegroup/zon-large
        * /imagegroup/zon-large__200x200

        Virtual Image:
        * /imagegroup/zon-large  # TODO
        * /imagegroup/zon-large__200x200
        * /imagegroup/zon-large-small  # only for previews in imagecutter

        JSON API:
        * /imagegroup/variants/zon-large

        """
        try:
            item = super(ImageGroup, self).__getitem__(key)
        except KeyError:
            item = self.create_variant_image(key)
        if key == self.master_image:
            zope.interface.alsoProvides(
                item, zeit.content.image.interfaces.IMasterImage)
        return item


class ImageGroupType(zeit.cms.type.TypeDeclaration):

    interface = zeit.content.image.interfaces.IImageGroup
    interface_type = zeit.content.image.interfaces.IImageType
    type = 'image-group'
    title = _('Image Group')
    addform = 'zeit.content.image.imagegroup.Add'

    def content(self, resource):
        ig = ImageGroup()
        ig.uniqueId = resource.id
        return ig

    def resource_body(self, content):
        return StringIO.StringIO()

    def resource_content_type(self, content):
        return 'httpd/unix-directory'


class LocalImageGroup(ImageGroupBase,
                      persistent.Persistent,
                      zope.app.container.contained.Contained):

    zope.interface.implements(zeit.content.image.interfaces.ILocalImageGroup)

    def __getitem__(self, key):
        repository = zeit.content.image.interfaces.IRepositoryImageGroup(self)
        if key in repository:
            return repository[key]
        return self.create_variant_image(key)

    # XXX Inheriting from UserDict.DictMixin would be much more sensible,
    # but that breaks browser/copyright.txt for reasons unknown. :-(
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


@grok.adapter(zeit.content.image.interfaces.IImageGroup)
@grok.implementer(zeit.content.image.interfaces.ILocalImageGroup)
def local_image_group_factory(context):
    lig = LocalImageGroup()
    lig.uniqueId = context.uniqueId
    lig.__name__ = context.__name__
    zeit.connector.interfaces.IWebDAVWriteProperties(lig).update(
        zeit.connector.interfaces.IWebDAVReadProperties(
            zope.security.proxy.removeSecurityProxy(context)))
    return lig


@grok.adapter(zeit.content.image.interfaces.ILocalImageGroup)
@grok.implementer(zeit.content.image.interfaces.IRepositoryImageGroup)
def find_repository_group(context):
    return zeit.cms.interfaces.ICMSContent(context.uniqueId)


class LocalSublocations(grok.Adapter):

    grok.context(zeit.content.image.interfaces.ILocalImageGroup)
    grok.implements(zope.location.interfaces.ISublocations)

    def sublocations(self):
        return []


@grok.adapter(zeit.content.image.interfaces.IImageGroup, name='image')
@grok.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    image = lxml.objectify.E.image()
    image.set('base-id', context.uniqueId)

    type = ''
    for sub_image_name in context:
        if '.' not in sub_image_name:
            continue
        base, ext = sub_image_name.rsplit('.', 1)
        if base.endswith('x140'):
            # This is deciding
            type = ext
            break
        if not type:
            # Just remember the first type
            type = ext

    image.set('type', type)
    # The image reference can be seen like an element in a feed. Let the magic
    # update the xml node.
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(image)
    return image


@grok.adapter(zeit.content.image.interfaces.IImageGroup)
@grok.implementer(zeit.content.image.interfaces.IMasterImage)
def find_master_image(context):
    if context.master_image:
        return context.get(context.master_image)
