# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import sprout.htmlsubset

MARKUP_BASE = ('i', 'em')
MARKUP_LINK = ('a', )
MARKUP_BR = ('br',)

MARKUP_HEADING = MARKUP_BASE + MARKUP_LINK + MARKUP_BR

# Replace left hand side tags in user input by right hand side:
MARKUP_TEXT_TRANSLATION = {
    'i': 'em',
}


class AHandler(sprout.htmlsubset.SubsetHandler):
    """Handle <a>."""

    parsed_name = 'a'

    def startElementNS(self, name, qname, attrs):
        node = self.parent()
        child = node.ownerDocument.createElement('a')
        child.setAttribute('href', attrs[(None, 'href')])
        if attrs.has_key((None, 'target')):
            child.setAttribute('target', attrs[(None, 'target')])
        node.appendChild(child)
        self.setResult(child)

    def characters(self, data):
        node = self.result()
        node.appendChild(node.ownerDocument.createTextNode(data))


class BrHandler(sprout.htmlsubset.SubsetHandler):

    parsed_name = 'br'

    def startElementNS(self, name, qname, attrs):
        node = self.parent()
        child = node.ownerDocument.createElement('br')
        node.appendChild(child)
        self.setResult(child)


class MarkupTextHandler(sprout.htmlsubset.SubsetHandler):

    def startElementNS(self, name, qname, attrs):
        node = self.parent()
        child = node.ownerDocument.createElement(self.tree_name)
        node.appendChild(child)
        self.setResult(child)

    def characters(self, data):
        node = self.result()
        node.appendChild(node.ownerDocument.createTextNode(data))


def markupTextHandlerClass(parsed_name, tree_name):
    """Construct subclass able to handle element of name."""
    return type('%s_handler_class' % parsed_name, (MarkupTextHandler,),
                {'tree_name': tree_name, 'parsed_name': parsed_name})


def create_cms_subset():
    subset = sprout.htmlsubset.Subset()
    for name in MARKUP_BASE:
        handler = markupTextHandlerClass(
            name, MARKUP_TEXT_TRANSLATION.get(name, name))
        element = sprout.htmlsubset.Element(
            name, [], [], MARKUP_HEADING, handler)
        subset.registerElement(element)
    subset.registerElement(
        sprout.htmlsubset.Element(
            'a', ['href'], ['target'], MARKUP_BASE, AHandler))
    subset.registerElement(
        sprout.htmlsubset.Element('br', [], [], [], BrHandler))
    # 'block' tag is used to produce fake surrounding tag, real one will
    # be something else. Need to register allowed elements for it
    subset.registerElement(
        sprout.htmlsubset.Element(
            'block', [], [], MARKUP_HEADING, sprout.htmlsubset.BlockHandler))
    return subset


CMS_SUBSET = create_cms_subset()
