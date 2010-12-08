# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import copy
import gocept.lxml.interfaces
import grokcore.component
import lxml.etree
import lxml.html
import lxml.objectify
import xml.sax.saxutils
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component


# XXX The factory registration could be much easier with a custom grokker for
# the Element classes itself.


class Paragraph(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IParagraph)
    type = 'p'

    @property
    def text(self):
        # The copy.copy magically removes unnecessary namespace declarations.
        p_text = self.xml.text or ''
        text = xml.sax.saxutils.escape(p_text) + ''.join(
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
        p.tag = self.type
        self.xml.getparent().replace(self.xml, p)
        self.xml = p


class ParagraphFactory(zeit.content.article.edit.block.BlockFactory):

    produces = Paragraph
    title = _('<p>')


class UnorderedList(Paragraph):

    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IUnorderedList)
    type = 'ul'


class UnorderedListFactory(zeit.content.article.edit.block.BlockFactory):

    produces = UnorderedList
    title = _('<ul>')


class OrderedList(Paragraph):

    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IOrderedList)
    type = 'ol'


class OrderedListFactory(zeit.content.article.edit.block.BlockFactory):

    produces = OrderedList
    title = _('<ol>')


class Intertitle(Paragraph):

    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IIntertitle)
    type = 'intertitle'


class IntertitleFactory(zeit.content.article.edit.block.BlockFactory):

    produces = Intertitle
    title = _('<intertitle>')
