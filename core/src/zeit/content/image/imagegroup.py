from zeit.cms.i18n import MessageFactory as _
import StringIO
import grokcore.component as grok
import hashlib
import lxml.objectify
import persistent
import urlparse
import z3c.traverser.interfaces
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
        'variants',
        writeable=zeit.cms.content.interfaces.WRITEABLE_LIVE)

    @property
    def variants(self):
        if self._variants is None:
            return {}
        return self._variants

    @variants.setter
    def variants(self, value):
        self._variants = value

    def create_variant_image(self, key, source=None):
        variants = zeit.content.image.interfaces.IVariants(self)
        key = self._verify_signature(key)
        if '__' in key:
            variant = variants.get_by_size(key)
            size = [int(x) for x in key.split('__')[1].split('x')]
        else:
            variant = variants.get_by_name(key)
            size = None

        if variant is None:
            raise KeyError(key)

        if source is None:
            source = zeit.content.image.interfaces.IMasterImage(self, None)
        if source is None:
            raise KeyError(key)

        repository = zeit.content.image.interfaces.IRepositoryImageGroup(self)
        if variant.name in repository:
            return repository[variant.name]

        image = zeit.content.image.interfaces.ITransform(
            source).create_variant_image(variant, size=size)
        image.__name__ = key
        image.__parent__ = self
        return image

    def _verify_signature(self, key):
        if not self._variant_secret:
            return key
        try:
            parts = key.split('__')
            if len(parts) == 2:
                name, signature = parts
                width = height = None
                stripped = name
            elif len(parts) == 3:
                name, size, signature = parts
                width, height = size.split('x')
                stripped = '{name}__{size}'.format(name=name, size=size)
            if verify_signature(
                    name, width, height, self._variant_secret, signature):
                return stripped
        except:
            pass
        raise KeyError(key)

    def variant_url(self, name, width=None, height=None, thumbnail=False):
        path = urlparse.urlparse(self.uniqueId).path
        if path.endswith('/'):
            path = path[:-1]
        if thumbnail:
            name = 'thumbnail/%s' % name
        if width is None or height is None:
            url = '{path}/{name}'.format(path=path, name=name)
        else:
            url = '{path}/{name}__{width}x{height}'.format(
                path=path, name=name, width=width, height=height)
        if self._variant_secret:
            url += '__{signature}'.format(signature=compute_signature(
                name, width, height, self._variant_secret))
        return url

    @property
    def _variant_secret(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.image')
        return config.get('variant-secret')


def compute_signature(name, width, height, secret):
    return hashlib.sha1(':'.join(
        [str(x) for x in [name, width, height, secret]])).hexdigest()


def verify_signature(name, width, height, secret, signature):
    return signature == compute_signature(name, width, height, secret)


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
        * /imagegroup/zon-large
        * /imagegroup/zon-large__200x200

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

    def __contains__(self, key):
        return self.get(key) is not None

    def __setitem__(self, key, value):
        repository = zeit.content.image.interfaces.IRepositoryImageGroup(self)
        repository[key] = value


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


class ThumbnailTraverser(object):

    zope.interface.implements(z3c.traverser.interfaces.IPluggableTraverser)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        if name != 'thumbnail':
            raise zope.publisher.interfaces.NotFound(
                self.context, name, request)
        return zeit.content.image.interfaces.IThumbnails(self.context)


class Thumbnails(grok.Adapter):

    grok.context(zeit.content.image.interfaces.IRepositoryImageGroup)
    grok.implements(zeit.content.image.interfaces.IThumbnails)

    SOURCE_IMAGE_PREFIX = 'thumbnail-source'
    THUMBNAIL_WIDTH = 1000

    def __getitem__(self, key):
        if self.master_image is None:
            raise KeyError(key)
        return self.context.create_variant_image(
            key, source=self.source_image)

    @property
    def source_image_name(self):
        return '%s-%s' % (self.SOURCE_IMAGE_PREFIX, self.master_image.__name__)

    @property
    def source_image(self):
        if self.source_image_name in self.context:
            return self.context[self.source_image_name]
        if self.master_image.getImageSize()[0] <= self.THUMBNAIL_WIDTH:
            return self.master_image
        lockable = zope.app.locking.interfaces.ILockable(self.context, None)
        # XXX 1. mod_dav does not allow LOCK of a member in a locked collection
        # even though the WebDAV spec reads as if that should be possible.
        # 2. zeit.connector has some kind of bug where it loses the property
        # cache of the collection upon that error, so it thinks the collection
        # is empty from then on out (only refresh-cache helps).
        if lockable is not None and not lockable.locked():
            return self._create_source_image()
        else:
            return self.master_image

    def _create_source_image(self):
        image = zeit.content.image.interfaces.ITransform(
            self.master_image).resize(width=self.THUMBNAIL_WIDTH)
        self.context[self.source_image_name] = image
        return self.context[self.source_image_name]

    @property
    def master_image(self):
        return zeit.content.image.interfaces.IMasterImage(self.context, None)


@grok.subscribe(
    zeit.content.image.interfaces.IImage,
    zope.lifecycleevent.IObjectAddedEvent)
def create_thumbnail_source_on_add(context, event):
    group = context.__parent__
    if not zeit.content.image.interfaces.IRepositoryImageGroup.providedBy(
            group):
        return
    if group.master_image != context.__name__:
        return
    thumbnails = zeit.content.image.interfaces.IThumbnails(group)
    if thumbnails.master_image:
        thumbnails.source_image
