import copy

import grokcore.component as grok
import lxml.builder
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.infobox.interfaces


@zope.interface.implementer(zeit.content.infobox.interfaces.IInfobox, zeit.cms.interfaces.IAsset)
class Infobox(zeit.cms.content.metadata.CommonMetadata):
    default_template = '<container layout="artbox" label="info" />'

    supertitle = zeit.cms.content.property.ObjectPathProperty('.supertitle')

    @property
    def contents(self):
        result = []
        for node in self.xml.findall('block'):
            text_node = node.find('text')
            if text_node is None:
                text_node = lxml.builder.E.text()
            elif text_node.text and text_node.text.strip():
                text_node = copy.copy(text_node)
                # There is text which is not wrapped into a node. Wrap it.
                text_node = lxml.builder.E.text(
                    lxml.builder.E.p(text_node.text, *text_node.getchildren())
                )
            text = self.html_converter.to_html(text_node)
            result.append((node.find('title').text, text))
        return tuple(result)

    @contents.setter
    def contents(self, value):
        for node in self.xml.findall('block'):
            self.xml.remove(node)
        for title, text in value:
            text_node = lxml.builder.E.text()
            self.html_converter.from_html(text_node, text)
            self.xml.append(lxml.builder.E.block(lxml.builder.E.title(title), text_node))
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
