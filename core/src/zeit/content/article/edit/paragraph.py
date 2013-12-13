# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import copy
import grokcore.component as grok
import lxml.etree
import lxml.html.clean
import lxml.html.soupparser
import lxml.objectify
import xml.sax.saxutils
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


def keep_allowed_tags(tree, allowed_tags):
    # XXX from an architecture point of view this should be done on the client
    # (see javascript:zeit.content.article.html), but being able to use
    # lxml.html.clean is just so convenient.
    remove_tags = lxml.html.clean.Cleaner(
        allow_tags=set(allowed_tags), remove_unknown_tags=False)
    remove_tags(tree)
    return tree


inline_tags = ['a', 'br', 'i', 'em', 'strong', 'b', 'u']


class ParagraphBase(zeit.edit.block.SimpleElement):

    grok.baseclass()

    area = zeit.content.article.edit.interfaces.IEditableBody
    allowed_tags = inline_tags

    def keep_allowed_tags(self, tree):
        return keep_allowed_tags(tree, self.allowed_tags)

    def _to_xml(self, value):
        p = lxml.html.soupparser.fromstring(value)
        p = self.keep_allowed_tags(p)
        p.tag = self.type
        p.attrib.update(self.xml.attrib.items())
        # XXX do we want to set this as the default objectify parser in the
        # whole system?
        parser = lxml.objectify.makeparser(remove_blank_text=False)
        p = lxml.objectify.fromstring(lxml.etree.tostring(p), parser=parser)
        return p


class Paragraph(ParagraphBase):

    grok.implements(zeit.content.article.edit.interfaces.IParagraph)
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
        p = self._to_xml(value)
        self.xml.getparent().replace(self.xml, p)
        self.xml = p


class ParagraphFactory(zeit.content.article.edit.block.BlockFactory):

    produces = Paragraph


class UnorderedList(Paragraph):

    grok.implements(zeit.content.article.edit.interfaces.IUnorderedList)
    type = 'ul'
    allowed_tags = inline_tags + ['li']


class UnorderedListFactory(zeit.content.article.edit.block.BlockFactory):

    produces = UnorderedList


class OrderedList(UnorderedList):

    grok.implements(zeit.content.article.edit.interfaces.IOrderedList)
    type = 'ol'


class OrderedListFactory(zeit.content.article.edit.block.BlockFactory):

    produces = OrderedList


class Intertitle(Paragraph):

    grok.implements(zeit.content.article.edit.interfaces.IIntertitle)
    type = 'intertitle'


class IntertitleFactory(zeit.content.article.edit.block.BlockFactory):

    produces = Intertitle


class HTMLBlock(ParagraphBase):

    grok.implements(zeit.content.article.edit.interfaces.IHTMLBlock)
    type = 'htmlblock'

    title = zeit.cms.content.property.ObjectPathProperty('.title')

    @property
    def allowed_tags(self):
        return inline_tags + self.layout.allowed_tags

    @property
    def layout(self):
        for layout in (
                zeit.content.article.edit.interfaces.IHTMLBlock[
                    'layout'].source(self)):
            if layout.id == self.xml.get('layout'):
                return layout

    @layout.setter
    def layout(self, layout):
        self.xml.set('layout', layout.id)

    @property
    def contents(self):
        text = ''.join(
            lxml.etree.tostring(copy.copy(x))
            for x in self.xml.iterchildren() if x.tag != 'title')
        return unicode(text)

    @contents.setter
    def contents(self, value):
        for x in self.xml.iterchildren():
            if x.tag == 'title':
                continue
            self.xml.remove(x)
        if value:
            value = self._to_xml(value)
            for x in value.iterchildren():
                self.xml.append(x)


class HTMLBlockFactory(zeit.content.article.edit.block.BlockFactory):

    produces = HTMLBlock
    title = _('HTML block')
