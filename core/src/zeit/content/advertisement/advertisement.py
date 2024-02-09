import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.advertisement.interfaces


@zope.interface.implementer(
    zeit.content.advertisement.interfaces.IAdvertisement, zeit.cms.interfaces.IEditorialContent
)
class Advertisement(zeit.cms.content.xmlsupport.XMLContentBase):
    default_template = '<advertisement><head/><body/></advertisement>'

    supertitle = zeit.cms.content.property.ObjectPathProperty(
        '.body.supertitle', zeit.content.advertisement.interfaces.IAdvertisement['supertitle']
    )
    title = zeit.cms.content.property.ObjectPathProperty(
        '.body.title', zeit.content.advertisement.interfaces.IAdvertisement['title']
    )
    text = zeit.cms.content.property.ObjectPathProperty(
        '.body.text', zeit.content.advertisement.interfaces.IAdvertisement['text']
    )
    button_text = zeit.cms.content.property.ObjectPathProperty(
        '.body.button_text', zeit.content.advertisement.interfaces.IAdvertisement['button_text']
    )
    button_color = zeit.cms.content.property.ObjectPathProperty(
        '.body.button_color', zeit.content.advertisement.interfaces.IAdvertisement['button_color']
    )
    image = zeit.cms.content.reference.SingleResource('.head.image', 'image')
    url = zeit.cms.content.property.ObjectPathProperty(
        '.body.url', zeit.content.advertisement.interfaces.IAdvertisement['url']
    )


class AdvertisementType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Advertisement
    interface = zeit.content.advertisement.interfaces.IAdvertisement
    title = _('Publisher advertisement')
    type = 'advertisement'
