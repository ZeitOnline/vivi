# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import BeautifulSoup
import lxml.etree
import lxml.html.soupparser
import lxml.objectify
import zope.schema.interfaces


def applySchemaData(context, schema, data, omit=()):
    omit = set(omit)
    for name in schema:
        if name in omit:
            continue
        field = schema[name]
        if not zope.schema.interfaces.IField.providedBy(field):
            continue
        value = data.get(name, field.default)
        setattr(context, name, value)


def objectify_soup_fromstring(text):
    # like lxml.objectify.fromstring, but with BeautifulSoup as backend.
    # The basic idea is simple: pass an objectify-enabled makeelement to
    # lxml.html.soupparser. The devil is in the details, however.

    # soupparser insists on modifiying node.text, which lxml.objectify
    # does not allow, so we need to use objectify-internal API to do it.
    orig_append = lxml.html.soupparser._append_text

    def _objectify_append_text(node, element, text):
        if text == '\n':
            # preserve whitespace behaviour similar to lxml.objectify
            return
        if element is None:
            node._setText((node.text or '') + text)
        else:
            orig_append(node, element, text)

    try:
        lxml.html.soupparser._append_text = _objectify_append_text

        # I'd just like to use the default parser from lxml.objectify, but
        # that's inaccessible since it's not in __all__, so we need to recreate
        # it manually.
        objectify_parser = lxml.etree.XMLParser()
        objectify_parser.set_element_class_lookup(
            lxml.objectify.ObjectifyElementClassLookup())

        # we need an XML parser (since the input might contain non-HTML which
        # we want to process), which can't create elements named '[document]',
        # unlike the HTML parser which happily does that (strange!),
        # thus we have to insist on a proper root tag name here.
        soup = BeautifulSoup.BeautifulSoup(text)
        soup.name = 'root'

        trees = lxml.html.soupparser.convert_tree(
            soup, makeelement=objectify_parser.makeelement)
        return trees[0]
    finally:
        lxml.html.soupparser._append_text = orig_append
