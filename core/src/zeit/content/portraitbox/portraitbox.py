
from zeit.cms.i18n import MessageFactory as _
import lxml.builder
import lxml.objectify
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.portraitbox.interfaces
import zeit.wysiwyg.html
import zope.interface


class Portraitbox(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(zeit.content.portraitbox.interfaces.IPortraitbox,
                              zeit.cms.interfaces.IAsset)

    default_template = (
        u'<container layout="artbox" label="portrait" '
        u'xmlns:py="http://codespeak.net/lxml/objectify/pytype" />')

    name = zeit.cms.content.property.ObjectPathProperty('.block.title')
    text = zeit.cms.content.property.Structure('.block.text')
    image = zeit.cms.content.reference.SingleResource(
        '.block.image', xml_reference_name='image')


class PortraiboxType(zeit.cms.type.XMLContentTypeDeclaration):

    interface = zeit.content.portraitbox.interfaces.IPortraitbox
    type = 'portraitbox'
    factory = Portraitbox
    title = _('Portraitbox')


class PortraitboxHTMLContent(zeit.wysiwyg.html.HTMLContentBase):
    """HTML content of an article."""

    zope.component.adapts(zeit.content.portraitbox.interfaces.IPortraitbox)
    path = lxml.objectify.ObjectPath('.block.text')

    def get_tree(self):
        xml = zope.proxy.removeAllProxies(self.context.xml)
        text = self.path(xml, None)
        if text is None:
            self.path.setattr(xml, '')
            text = self.path(xml)
        elif len(text):
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
