# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import copy
import grokcore.component
import lxml.etree
import lxml.html.builder
import lxml.html.clean
import lxml.html.soupparser
import lxml.objectify
import xml.sax.saxutils
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zeit.edit.interfaces


def apply_filter(steps, tree):
    """Apply a series of filtering steps on an lxml tree.
    Filter steps can either work in-place or return a replacement tree.

    XXX it would be nice if this were uniformly in-place, but
    I guess keep_only_inline_tags can't be written like that.
    """
    for step in steps:
        result = step(tree)
        if result is not None:
            tree = result
    return tree


def escape_missing_href(tree):
    for el in tree.iter():
        if el.tag == 'a' and 'href' not in el.attrib:
            el.attrib['href'] = '#'


def keep_allowed_tags(tree, allowed_tags):
    remove_tags = lxml.html.clean.Cleaner(
        allow_tags=set(allowed_tags), remove_unknown_tags=False)
    # Cleaner requires the tree-root to have a parent, on which it assembles
    # the remaining parts (without the dropped tags)
    container = lxml.html.builder.E.body(tree)
    remove_tags(tree)
    return container


inline_tags = ['a', 'br', 'i', 'em', 'strong', 'b', 'u']


class Paragraph(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IParagraph)
    type = 'p'

    allowed_tags = inline_tags

    def __init__(self, *args, **kw):
        self.filter_steps = [
            self.keep_allowed_tags,
            escape_missing_href
        ]
        super(Paragraph, self).__init__(*args, **kw)

    def keep_allowed_tags(self, tree):
        return keep_allowed_tags(tree, self.allowed_tags)

    @property
    def text(self):
        # The copy.copy magically removes unnecessary namespace declarations.
        p_text = self.xml.text or ''
        text = xml.sax.saxutils.escape(p_text) + ''.join(
            lxml.etree.tostring(copy.copy(c)) for c in self.xml.iterchildren())
        return unicode(text)

    @text.setter
    def text(self, value):
        p = lxml.html.soupparser.fromstring(value)
        p = apply_filter(self.filter_steps, p)
        p.tag = self.type
        p.attrib.update(self.xml.attrib.items())
        p = lxml.objectify.fromstring(lxml.etree.tostring(p))
        self.xml.getparent().replace(self.xml, p)
        self.xml = p


class ParagraphFactory(zeit.content.article.edit.block.BlockFactory):

    produces = Paragraph
    title = _('<p>')


class UnorderedList(Paragraph):

    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IUnorderedList)
    type = 'ul'
    allowed_tags = inline_tags + ['li']


class UnorderedListFactory(zeit.content.article.edit.block.BlockFactory):

    produces = UnorderedList
    title = _('<ul>')


class OrderedList(UnorderedList):

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
