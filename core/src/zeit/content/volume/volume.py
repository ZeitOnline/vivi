from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.volume.interfaces
import zeit.workflow
import zope.interface


class Volume(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(
        zeit.content.volume.interfaces.IVolume,
        zeit.cms.interfaces.IEditorialContent)

    default_template = '<volume><head/><body/></volume>'

    zeit.cms.content.dav.mapProperties(
        zeit.content.volume.interfaces.IVolume,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('product', 'year', 'volume', 'teaserText',))

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


class VolumeType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Volume
    interface = zeit.content.volume.interfaces.IVolume
    title = _('Volume')
    type = 'volume'
