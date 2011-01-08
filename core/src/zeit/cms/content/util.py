# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import BeautifulSoup
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
    # There once (r18370) was a properly integrated variant that avoided an
    # addtional serialize/deserialize cycle, but it did not understand
    # namespaces, and could not be taught easily either, so it had to go.
    return lxml.objectify.fromstring(str(BeautifulSoup.BeautifulSoup(text)))
