from zeit.cms.i18n import MessageFactory as _
import UserDict
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.dav
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.volume.interfaces
import zeit.workflow.interfaces
import zope.interface
import zope.schema
import zope.security.proxy


class Volume(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(
        zeit.content.volume.interfaces.IVolume,
        zeit.cms.interfaces.IAsset)

    default_template = u"""\
        <volume xmlns:py="http://codespeak.net/lxml/objectify/pytype">
            <head/>
            <body/>
            <covers/>
        </volume>
    """

    year = zeit.cms.content.property.ObjectPathProperty(
        '.body.year', zeit.content.volume.interfaces.IVolume['year'])
    volume = zeit.cms.content.property.ObjectPathProperty(
        '.body.volume', zeit.content.volume.interfaces.IVolume['volume'])
    teaserText = zeit.cms.content.property.ObjectPathProperty(
        '.body.teaserText',
        zeit.content.volume.interfaces.IVolume['teaserText'])

    zeit.cms.content.dav.mapProperties(
        zeit.content.volume.interfaces.IVolume,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('date_digital_published',))

    _product_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        zeit.workflow.interfaces.WORKFLOW_NS,
        'product-id')

    @property
    def product(self):
        source = zeit.content.volume.interfaces.IVolume['product'].source(self)
        for value in source:
            if value.id == self._product_id:
                return value

    @product.setter
    def product(self, value):
        if self._product_id == value.id:
            return
        self._product_id = value.id if value is not None else None

    @property
    def covers(self):
        return zeit.content.volume.interfaces.IVolumeCovers(self)


class VolumeType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Volume
    interface = zeit.content.volume.interfaces.IVolume
    title = _('Volume')
    type = 'volume'


# XXX copied & adjusted from `zeit.content.author.author.BiographyQuestions`
class VolumeCovers(
        grok.Adapter,
        UserDict.DictMixin,
        zeit.cms.content.xmlsupport.Persistent):
    """Adapter to store `IImageGroup` references inside XML of `Volume`.

    The adapter interferes with the zope.formlib by overwriting setattr/getattr
    and storing/retrieving the values on the XML of `Volume` (context).

    """

    grok.context(zeit.content.volume.interfaces.IVolume)
    grok.implements(zeit.content.volume.interfaces.IVolumeCovers)

    def __init__(self, context):
        """Set attributes using `object.__setattr__`, since we overwrite it."""
        object.__setattr__(self, 'context', context)
        object.__setattr__(self, 'xml', zope.security.proxy.getObject(
            context.xml))
        object.__setattr__(self, '__parent__', context)

    def __getitem__(self, key):
        node = self.xml.xpath('//covers/cover[@id="%s"]' % key)
        uniqueId = node[0].get('href') if node else None
        return zeit.cms.interfaces.ICMSContent(uniqueId, None)

    def __setitem__(self, key, value):
        node = self.xml.xpath('//covers/cover[@id="%s"]' % key)
        if node:
            self.xml.covers.remove(node[0])
        if value:
            node = lxml.objectify.E.cover(id=key, href=value.uniqueId)
            lxml.objectify.deannotate(node[0], cleanup_namespaces=True)
            self.xml.covers.append(node)
        super(VolumeCovers, self).__setattr__('_p_changed', True)

    def keys(self):
        return list(zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(self))

    def title(self, key):
        return zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(
            self).title(key)

    # XXX Why does the formlib work without an explicit security declaration?

    def __getattr__(self, key):
        """Interfere with zope.formlib and retrieve content via getitem.

        Since the formlib only accesses fields from VOLUME_COVER_SOURCE, i.e.
        ``self.keys()``, we forward other calls to the "normal" implementation
        of ``__getattr__``.

        """
        if key in self.keys():
            return self.get(key)
        return super(VolumeCovers, self).__getattr__(key)

    def __setattr__(self, key, value):
        """Interfere with zope.formlib and store content via setitem.

        Since the formlib only accesses fields from VOLUME_COVER_SOURCE, i.e.
        ``self.keys()``, we forward other calls to the "normal" implementation
        of ``__setattr__``.

        """
        if key in self.keys():
            self[key] = value
        return super(VolumeCovers, self).__setattr__(key, value)


@grok.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@grok.implementer(zeit.content.volume.interfaces.IVolume)
def retrieve_volume_using_info_from_metadata(context):
    if (context.year is None or context.volume is None or
            context.product is None or not context.product.volume or
            context.product.location is None):
        return None
    uniqueId = context.product.location.format(
        year=context.year,
        name=str(context.volume).rjust(2, '0'))
    return zeit.cms.interfaces.ICMSContent(uniqueId, None)
