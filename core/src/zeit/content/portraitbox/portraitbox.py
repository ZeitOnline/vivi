import lxml.builder
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.portraitbox.interfaces
import zeit.wysiwyg.html


@zope.interface.implementer(
    zeit.content.portraitbox.interfaces.IPortraitbox, zeit.cms.interfaces.IAsset
)
class Portraitbox(zeit.cms.content.xmlsupport.XMLContentBase):
    default_template = '<container layout="artbox" label="portrait" />'

    name = zeit.cms.content.property.ObjectPathProperty('.block.title')
    text = zeit.cms.content.property.Structure('.block.text')
    image = zeit.cms.content.reference.SingleResource('.block.image', xml_reference_name='image')


class PortraiboxType(zeit.cms.type.XMLContentTypeDeclaration):
    interface = zeit.content.portraitbox.interfaces.IPortraitbox
    type = 'portraitbox'
    factory = Portraitbox
    title = _('Portraitbox')


@zope.component.adapter(zeit.content.portraitbox.interfaces.IPortraitbox)
class PortraitboxHTMLContent(zeit.wysiwyg.html.HTMLContentBase):
    """HTML content of an article."""

    def get_tree(self):
        xml = zope.proxy.removeAllProxies(self.context.xml)
        text = xml.find('block/text')
        if text is None:
            parent = xml.find('block')
            if parent is None:
                parent = lxml.builder.E.block()
                xml.append(parent)
            text = lxml.builder.E.text()
            parent.append(text)
        elif text.getchildren():
            for child in text.iterchildren():
                if child.tag == 'p':
                    break
            else:
                # There was no <p> node. Wrap the entire contents of text into
                # a new <p>
                children = [text.text]
                for child in text.getchildren():
                    children.append(child)
                    text.remove(child)
                text.append(lxml.builder.E.p(*children))
        return text
