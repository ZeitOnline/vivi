# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import sprout.htmlsubset
import sprout.silvasubset

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


def create_cms_subset():
    subset = sprout.htmlsubset.Subset()
    for name in MARKUP_BASE:
        handler = sprout.silvasubset.markupTextHandlerClass(
            name, MARKUP_TEXT_TRANSLATION.get(name, name))
        element = sprout.htmlsubset.Element(
            name, [], [], MARKUP_HEADING, handler)
        subset.registerElement(element)
    subset.registerElement(
        sprout.htmlsubset.Element(
            'a', ['href'], ['target'], MARKUP_BASE, AHandler))
    subset.registerElement(
        sprout.htmlsubset.Element('br', [], [], [],
                                  sprout.silvasubset.BrHandler))
    # 'block' tag is used to produce fake surrounding tag, real one will
    # be something else. Need to register allowed elements for it
    subset.registerElement(
        sprout.htmlsubset.Element(
            'block', [], [], MARKUP_HEADING, sprout.htmlsubset.BlockHandler))
    return subset


CMS_SUBSET = create_cms_subset()
