import grokcore.component as grok
import lxml.objectify
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.infobox.interfaces


@zope.interface.implementer(zeit.content.infobox.interfaces.IInfobox, zeit.cms.interfaces.IAsset)
class Infobox(zeit.cms.content.metadata.CommonMetadata):
    default_template = (
        '<container layout="artbox" label="info" '
        'xmlns:py="http://codespeak.net/lxml/objectify/pytype" '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" />'
    )

    supertitle = zeit.cms.content.property.ObjectPathProperty('.supertitle')

    @property
    def contents(self):
        result = []
        for node in self.xml.findall('block'):
            text_node = node.find('text')
            if text_node is None:
                text_node = lxml.objectify.E.text()
            elif text_node.text:
                # There is text which is not wrapped into a node. Wrap it.
                text_node = lxml.objectify.E.text(
                    lxml.objectify.E.p(text_node.text, *text_node.getchildren())
                )
            text = self.html_converter.to_html(text_node)
            result.append((str(node['title']), text))
        return tuple(result)

    @contents.setter
    def contents(self, value):
        for node in self.xml.findall('block'):
            self.xml.remove(node)
        for title, text in value:
            text_node = lxml.objectify.E.text()
            self.html_converter.from_html(text_node, text)
            self.xml.append(lxml.objectify.E.block(lxml.objectify.E.title(title), text_node))
        self._p_changed = True

    @property
    def html_converter(self):
        return zeit.wysiwyg.interfaces.IHTMLConverter(self)


class InfoboxType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Infobox
    interface = zeit.content.infobox.interfaces.IInfobox
    type = 'infobox'
    title = _('Infobox')


@grok.implementer(zeit.content.infobox.interfaces.IDebate)
class Debate(zeit.cms.content.dav.DAVPropertiesAdapter):
    action_url = zeit.cms.content.dav.DAVProperty(
        zeit.content.infobox.interfaces.IDebate['action_url'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'debate_action_url',
    )
