# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import copy
import gocept.lxml.interfaces
import grokcore.component
import lxml.etree
import lxml.html
import lxml.objectify
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component


class Paragraph(zeit.edit.block.Element,
                grokcore.component.MultiAdapter):

    grokcore.component.adapts(
      zeit.content.article.edit.interfaces.IEditableBody,
      gocept.lxml.interfaces.IObjectified)
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IParagraph)
    grokcore.component.provides(
        zeit.content.article.edit.interfaces.IParagraph)

    type = 'p'
    grokcore.component.name(type)

    @property
    def text(self):
        # The copy.copy magically removes unnecessary namespace declarations.
        p_text = self.xml.text or ''
        text = p_text + ''.join(
            lxml.etree.tostring(copy.copy(c)) for c in self.xml.iterchildren())
        return unicode(text)

    @text.setter
    def text(self, value):
        # XXX I guess we need to munge at least <a href> here in some way.
        try:
            p = lxml.objectify.XML(
                lxml.etree.tostring(
                    lxml.html.fromstring('<%s>%s</%s>' % (
                        self.type, value, self.type))))
        except lxml.etree.XMLSyntaxError:
            raise ValueError('No valid XML: %s' % (value,))
        p.attrib.update(self.xml.attrib.items())
        self.xml.getparent().replace(self.xml, p)
        self.xml = p


class ParagraphFactory(zeit.content.article.edit.block.BlockFactory):

    element_type = Paragraph.type
    title = _('<p>')
    grokcore.component.name(element_type)

    def get_xml(self):
        return lxml.objectify.E.p()


class UnorderedList(Paragraph):

    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IUnorderedList)
    grokcore.component.provides(
        zeit.content.article.edit.interfaces.IUnorderedList)
    type = 'ul'
    grokcore.component.name(type)


class UnorderedListFactory(zeit.content.article.edit.block.BlockFactory):

    element_type = UnorderedList.type
    title = _('<ul>')
    grokcore.component.name(element_type)

    def get_xml(self):
        return lxml.objectify.E.ul()
