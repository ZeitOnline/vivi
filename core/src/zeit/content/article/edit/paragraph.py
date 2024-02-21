import copy
import xml.sax.saxutils

import grokcore.component as grok
import lxml.etree
import lxml.html.clean
import lxml.html.soupparser

import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


def keep_allowed_tags(tree, allowed_tags):
    # XXX from an architecture point of view this should be done on the client
    # (see javascript:zeit.content.article.html), but being able to use
    # lxml.html.clean is just so convenient.
    remove_tags = lxml.html.clean.Cleaner(allow_tags=set(allowed_tags), remove_unknown_tags=False)
    remove_tags(tree)
    return tree


inline_tags = ['a', 'br', 'i', 'em', 'strong', 'b', 'u']


class ParagraphBase(zeit.content.article.edit.block.Block):
    grok.baseclass()

    area = zeit.content.article.edit.interfaces.IEditableBody
    allowed_tags = inline_tags

    def keep_allowed_tags(self, tree):
        return keep_allowed_tags(tree, self.allowed_tags)

    def _to_xml(self, value):
        value = '<p>%s</p>' % value
        p = lxml.html.soupparser.fromstring(value)
        p = self.keep_allowed_tags(p)
        p.tag = self.type
        p.attrib.update(self.xml.attrib.items())
        p = lxml.etree.fromstring(lxml.etree.tostring(p))
        return p


@grok.implementer(zeit.content.article.edit.interfaces.IParagraph)
class Paragraph(ParagraphBase):
    type = 'p'

    @property
    def text(self):
        # The copy.copy magically removes unnecessary namespace declarations.
        p_text = self.xml.text or ''
        text = xml.sax.saxutils.escape(p_text) + ''.join(
            lxml.etree.tostring(copy.copy(c), encoding=str) for c in self.xml.iterchildren()
        )
        return text

    @text.setter
    def text(self, value):
        p = self._to_xml(value)
        self.xml.getparent().replace(self.xml, p)
        self.xml = p


class ParagraphFactory(zeit.content.article.edit.block.BlockFactory):
    produces = Paragraph


@grok.implementer(zeit.content.article.edit.interfaces.IParagraph)
class LegacyInitialParagraph(Paragraph):
    type = 'initial'


class LegacyInitialParagraphFactory(zeit.content.article.edit.block.BlockFactory):
    produces = LegacyInitialParagraph


@grok.implementer(zeit.content.article.edit.interfaces.IUnorderedList)
class UnorderedList(Paragraph):
    type = 'ul'
    allowed_tags = inline_tags + ['li']


class UnorderedListFactory(zeit.content.article.edit.block.BlockFactory):
    produces = UnorderedList


@grok.implementer(zeit.content.article.edit.interfaces.IOrderedList)
class OrderedList(UnorderedList):
    type = 'ol'


class OrderedListFactory(zeit.content.article.edit.block.BlockFactory):
    produces = OrderedList


@grok.implementer(zeit.content.article.edit.interfaces.IIntertitle)
class Intertitle(Paragraph):
    type = 'intertitle'


class IntertitleFactory(zeit.content.article.edit.block.BlockFactory):
    produces = Intertitle
