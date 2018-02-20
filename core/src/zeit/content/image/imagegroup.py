from math import ceil
from zeit.cms.i18n import MessageFactory as _
from zeit.content.image.interfaces import IMAGE_NAMESPACE, VIEWPORT_SOURCE
import PIL.ImageColor
import StringIO
import collections
import grokcore.component as grok
import lxml.objectify
import os.path
import persistent
import re
import sys
import urlparse
import z3c.traverser.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.type
import zeit.connector.interfaces
import zeit.content.image.interfaces
import zeit.content.image.variant
import zope.app.container.contained
import zope.interface
import zope.lifecycleevent.interfaces
import zope.location.interfaces
import zope.security.proxy


# Use an object whose bool() evaluates to False, so it works in conditionals.
INVALID_SIZE = collections.namedtuple('InvalidSize', [])()


def get_viewport_from_key(key):
    """If key contains `__mobile`, retrieve viewport `mobile` else None."""
    for segment in key.split('__')[1:]:
        if segment in zeit.content.image.interfaces.VIEWPORT_SOURCE(None):
            return segment
    return None


class ImageGroupBase(object):

    zope.interface.implements(zeit.content.image.interfaces.IImageGroup)

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageGroup,
        IMAGE_NAMESPACE,
        ('display_type',),
        use_default=True)

    _master_images = zeit.cms.content.dav.DAVProperty(
        zeit.content.image.interfaces.IImageGroup['master_images'],
        IMAGE_NAMESPACE,
        'master_images')

    _variants = zeit.cms.content.dav.DAVProperty(
        zeit.content.image.interfaces.IImageGroup['variants'],
        IMAGE_NAMESPACE,
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

    @property
    def master_images(self):
        """Return tuple of master images and which viewport they are used for.

        If empty, we probably have an old image group. Read old master_image
        from DAV property for backward compatibility. Assume the first viewport
        in VIEWPORT_SOURCE should be used for the first master image.

        """
        if self._master_images:
            return self._master_images

        # read first viewport from source to use as default viewport
        viewport = next(iter(VIEWPORT_SOURCE(self)))
        # try to read master_image from DAV properties for bw compat
        properties = zeit.connector.interfaces.IWebDAVReadProperties(self)
        master_image = properties.get(('master_image', IMAGE_NAMESPACE), None)
        return ((viewport, master_image),) if master_image else ()

    @master_images.setter
    def master_images(self, value):
        self._master_images = value

    @property
    def master_image(self):
        """Return first image of `master_images` as default master image."""
        return self.master_images[0][1] if self.master_images else None

    def master_image_for_viewport(self, viewport):
        repository = zeit.content.image.interfaces.IRepositoryImageGroup(self)
        for view, name in self.master_images:
            if viewport == view:
                if name in repository:
                    return repository[name]
        return zeit.content.image.interfaces.IMasterImage(self, None)

    def create_variant_image(self, key, source=None):
        """Retrieve Variant and create an image according to options in URL.

        See ImageGroup.__getitem__ for allowed URLs.

        """
        repository = zeit.content.image.interfaces.IRepositoryImageGroup(self)
        variant = self.get_variant_by_key(key)
        size = self.get_variant_size(key)
        fill = self.get_variant_fill(key)
        viewport = self.get_variant_viewport(key)
        scale = self.get_scale(key)
        # The scale should not influence the variant selection, so we apply it
        # only _after_ the variant has been selected (otherwise we simply could
        # pass in a larger size and be done with it ;).
        if scale and size and (0.5 <= scale <= 3.0):
            size = [int(ceil(x * scale)) for x in size]

        # Make sure no invalid or redundant modifiers were provided
        values = [variant.name, size, fill, viewport, scale]
        if len([x for x in values if x]) != len(key.split('__')):
            raise KeyError(key)

        # Always prefer materialized images with matching name
        if source is None and variant.name in repository:
            source = repository[variant.name]
            if size is None:
                size = source.getImageSize()

        # BBB Legacy ImageGroups should still return their materialized
        # variants (for CP editor).
        elif source is None and variant.legacy_name is not None:
            for name in repository:
                if variant.legacy_name in name:
                    source = repository[name]
                    if size is None:
                        size = source.getImageSize()

        # Prefer a master image that was configured for given viewport.
        elif source is None and viewport is not None:
            source = self.master_image_for_viewport(viewport)

        # Our default transformation source should be the master image.
        if source is None:
            source = zeit.content.image.interfaces.IMasterImage(self, None)
        if source is None:
            raise KeyError(key)

        # Set size to max_size if Variant has max_size defined in XML and size
        # was neither given in URL nor implied by a legacy variant.
        if size is None:
            if variant.legacy_size is not None:
                size = variant.legacy_size
            elif variant.max_width < sys.maxint > variant.max_height:
                size = [variant.max_width, variant.max_height]

        # Be defensive about missing meta files, so source could not be
        # recognized as an image (for zeit.web)
        transform = zeit.content.image.interfaces.ITransform(source, None)
        if transform is None:
            return None

        image = transform.create_variant_image(variant, size, fill)
        image.__name__ = key
        image.__parent__ = self
        image.uniqueId = u'%s%s' % (self.uniqueId, key)
        image.variant_source = source.__name__
        return image

    def get_variant_size(self, key):
        """If key contains `__120x90`, retrieve size as [120, 90] else None"""
        for segment in key.split('__')[1:]:
            try:
                width, height = [int(x) for x in segment.split('x')]
            except (IndexError, ValueError):
                continue
            else:
                if any(i <= 0 for i in [width, height]):
                    return INVALID_SIZE
                return [width, height]
        return None

    def get_variant_fill(self, key):
        """If key contains `__blue`, retrieve fill as `0000ff` else None"""
        for segment in key.split('__')[1:]:
            for seg in set([segment, '#' + segment]):
                try:
                    fill = PIL.ImageColor.getrgb(seg)
                    return ''.join(format(i, '02x') for i in fill)
                except ValueError:
                    continue
        return None

    def get_variant_viewport(self, key):
        return get_viewport_from_key(key)

    def get_scale(self, key):
        """If key contains `scale_2.0` the function returns a scale of 2.0.
        If it is not possible to evaluate a scale because the key does not
        contain a scale, or the format is not valid, `None` is returned.
        """
        for segment in key.split('__')[1:]:
            seg = segment.split('scale_')
            try:
                return float(seg[1])
            except (IndexError, ValueError):
                continue
        return None

    def get_variant_by_key(self, key):
        """Retrieve Variant by using as much information as given in key."""
        variant = self.get_variant_by_size(key)
        if variant is not None:
            return variant

        variant = self.get_variant_by_name(key)
        if variant is not None:
            return variant

        raise KeyError(key)

    def get_variant_by_name(self, key):
        """Select the biggest Variant among those with the given name.

        The biggest Variant is the one that has no max-limit given or the
        biggest max-limit, if all Variants have a max-limit set.

        """
        name = key.split('__')[0]
        for variant in self.get_all_variants_with_name(name, reverse=True):
            return variant
        # BBB New ImageGroups must respond to the legacy names (for XSLT).
        for mapping in zeit.content.image.variant.LEGACY_VARIANT_SOURCE(self):
            if mapping['old'] in name:
                variant = self.get_variant_by_name(mapping['new'])
                if variant is None:
                    continue
                variant.legacy_name = mapping['old']
                variant.legacy_size = mapping['size']
                return variant
        return None

    def get_variant_by_size(self, key):
        """Select the Variant that has a matching name and matching size.

        The size does not need to be an exact fit. This method will try to find
        a Variant whose max-size is as small as possible, but bigger or equal
        than the size given in the key.

        """
        name = key.split('__')[0]
        candidates = self.get_all_variants_with_name(name)
        size = self.get_variant_size(key)
        if size is None:
            return None
        if size is INVALID_SIZE:
            return candidates[-1] if candidates else None
        for variant in candidates:
            if size[0] <= variant.max_width and size[1] <= variant.max_height:
                return variant
        return None

    def get_all_variants_with_name(self, name, reverse=False):
        """Return all Variants with a matching name, ordered by size."""
        variants = zeit.content.image.interfaces.IVariants(self)
        result = [v for v in variants.values() if name == v.name]
        result.sort(key=lambda x: (x.max_width, x.max_height), reverse=reverse)
        return result

    def variant_url(self, name, width=None, height=None,
                    fill_color=None, thumbnail=False):
        """Helper method to create URLs to Variant images."""
        path = urlparse.urlparse(self.uniqueId).path
        if path.endswith(u'/'):
            path = path[:-1]
        if thumbnail:
            name = u'%s/%s' % (Thumbnails.NAME, name)
        if width is None or height is None:
            url = u'{path}/{name}'.format(path=path, name=name)
        else:
            url = u'{path}/{name}__{width}x{height}'.format(
                path=path, name=name, width=width, height=height)
        if fill_color is not None:
            url += u'__{fill}'.format(fill=fill_color)
        return url


class ImageGroup(ImageGroupBase,
                 zeit.cms.repository.repository.Container):

    zope.interface.implements(
        zeit.content.image.interfaces.IRepositoryImageGroup)

    def __getitem__(self, key):
        """The following URLs may render images:

        Image is present on disk:
        * /imagegroup/imagegroup-540x304.jpg
        * /imagegroup/imagegroup-540x304__320x180
        * /imagegroup/540x304
        * /imagegroup/540x304__320x180
        * /imagegroup/zon-large
        * /imagegroup/zon-large__200x200

        Virtual Image:
        * /imagegroup/zon-large
        * /imagegroup/zon-large__200x200
        * /imagegroup/zon-large__200x200__0000ff
        * /imagegroup/zon-large__200x200__0000ff__mobile

        JSON API:
        * /imagegroup/variants/zon-large

        BBB compatibility:
        * Asking a new image group (without on-disk variants) for an old name
          (e.g. imagegroup-540x304.jpg, XSLT does this): maps old to new name
          via legacy-variant-source settings.
        * Asking an old image group for a new name: uses default focus point
          to generate the new variant.
          XXX Should we map to old on-disk variants instead?
        * Asking an old image group for an old name with the new syntax
          (CP editor does this): returns on-disk image.

        """
        __traceback_info__ = (self.uniqueId, key)
        try:
            item = super(ImageGroup, self).__getitem__(key)
        except KeyError:
            item = self.create_variant_image(key)
            if item is None:
                raise KeyError(key)
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
    factory = ImageGroup

    def content(self, resource):
        ig = self.factory()
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


class RepositorySublocations(grok.Adapter):

    grok.context(zeit.content.image.interfaces.IRepositoryImageGroup)
    grok.implements(zope.location.interfaces.ISublocations)

    def sublocations(self):
        for key in self.context.keys():
            if key in self.context:
                yield self.context[key]


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
    if context.master_image in context:
        return context[context.master_image]
    master_image = None
    for image in context.values():
        if zeit.content.image.interfaces.IImage.providedBy(
                image) and image.size > getattr(master_image, 'size', 0):
            master_image = image
            break
    return master_image


EXTERNAL_ID_PATTERN = re.compile('^[^\d]*([\d]+)[^\d]*$')


@grok.subscribe(
    zeit.content.image.interfaces.IImage,
    zope.lifecycleevent.interfaces.IObjectAddedEvent)
def guess_external_id(context, event):
    if not zeit.content.image.interfaces.IRepositoryImageGroup.providedBy(
            context.__parent__):
        return
    meta = zeit.content.image.interfaces.IImageMetadata(context.__parent__)
    if meta.external_id:
        return
    filename = context.__name__
    if filename.lower().startswith(u'rts'):  # Reuters
        meta.external_id = os.path.splitext(filename)[0]
    else:  # Getty, dpa
        match = EXTERNAL_ID_PATTERN.search(filename)
        if not match:
            return
        meta.external_id = match.group(1)


class ThumbnailTraverser(object):

    zope.interface.implements(z3c.traverser.interfaces.IPluggableTraverser)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        if name != Thumbnails.NAME:
            raise zope.publisher.interfaces.NotFound(
                self.context, name, request)
        return zeit.content.image.interfaces.IThumbnails(self.context)


class Thumbnails(grok.Adapter):

    grok.context(zeit.content.image.interfaces.IRepositoryImageGroup)
    grok.implements(zeit.content.image.interfaces.IThumbnails)

    NAME = 'thumbnails'
    SOURCE_IMAGE_PREFIX = 'thumbnail-source'
    THUMBNAIL_WIDTH = 1000

    def __getitem__(self, key):
        master_image = self.master_image(key)
        if master_image is None:
            raise KeyError(key)
        return self.context.create_variant_image(
            key, source=self.source_image(master_image))

    def source_image_name(self, master_image):
        return '%s-%s' % (self.SOURCE_IMAGE_PREFIX, master_image.__name__)

    def source_image(self, master_image):
        if master_image is None:
            return None
        if self.source_image_name(master_image) in self.context:
            return self.context[self.source_image_name(master_image)]
        if master_image.getImageSize()[0] <= self.THUMBNAIL_WIDTH:
            return master_image
        lockable = zope.app.locking.interfaces.ILockable(self.context, None)
        # XXX 1. mod_dav does not allow LOCK of a member in a locked collection
        # even though the WebDAV spec reads as if that should be possible.
        # 2. zeit.connector has some kind of bug where it loses the property
        # cache of the collection upon that error, so it thinks the collection
        # is empty from then on out (only refresh-cache helps).
        if lockable is not None and not lockable.locked():
            return self._create_source_image(master_image)
        else:
            return master_image

    def _create_source_image(self, master_image):
        image = zeit.content.image.interfaces.ITransform(
            master_image).resize(width=self.THUMBNAIL_WIDTH)
        self.context[self.source_image_name(master_image)] = image
        return self.context[self.source_image_name(master_image)]

    def master_image(self, key):
        viewport = get_viewport_from_key(key)
        if viewport:
            for view, name in self.context.master_images:
                if viewport == view:
                    return self.context[name]
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
    thumbnails.source_image(thumbnails.master_image(''))


@grok.subscribe(
    zeit.content.image.interfaces.IImageGroup,
    zeit.cms.repository.interfaces.IObjectReloadedEvent)
def refresh_thumbnail_source(context, event):
    if not zeit.content.image.interfaces.IRepositoryImageGroup.providedBy(
            context):
        return
    thumbnails = zeit.content.image.interfaces.IThumbnails(context)
    for name, image in context.items():
        if name.startswith(thumbnails.SOURCE_IMAGE_PREFIX):
            del context[name]
    for view, name in context.master_images:
        thumbnails.source_image(context[name])


@grok.subscribe(
    zeit.content.image.interfaces.IImage,
    zope.lifecycleevent.IObjectRemovedEvent)
def remove_thumbnail_source_on_delete(context, event):
    group = context.__parent__
    if not zeit.content.image.interfaces.IRepositoryImageGroup.providedBy(
            group):
        return
    thumbnails = zeit.content.image.interfaces.IThumbnails(group)
    thumbnail_name = thumbnails.source_image_name(context)
    if thumbnail_name in group:
        del group[thumbnail_name]
