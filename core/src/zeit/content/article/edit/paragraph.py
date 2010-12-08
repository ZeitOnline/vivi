# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import copy
import gocept.lxml.interfaces
import grokcore.component
import lxml.etree
import lxml.html
import lxml.objectify
import sprout.htmlsubset
import xml.sax.saxutils
import zeit.cms.content.cmssubset
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component


# XXX The factory registration could be much easier with a custom grokker for
# the Element classes itself.

class Subset(sprout.htmlsubset.Subset):

    def isAllowed(self, container_name, name):
        return True


paragraph_subset = zeit.cms.content.cmssubset.create_subset(
    zeit.cms.content.cmssubset.AHandler,
    zeit.cms.content.cmssubset.BrHandler,
    zeit.cms.content.cmssubset.markupTextHandlerClass('i', 'em'),
    zeit.cms.content.cmssubset.markupTextHandlerClass('em'),
    zeit.cms.content.cmssubset.markupTextHandlerClass('strong'),
    zeit.cms.content.cmssubset.markupTextHandlerClass('b', 'strong'),
    zeit.cms.content.cmssubset.markupTextHandlerClass('u'),
    subset_class=Subset)


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
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString('<p/>')
        value = paragraph_subset.parse(value, dom.firstChild)
        try:
            p = lxml.objectify.XML(value.toxml())
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
