# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

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
    soup = BeautifulSoup.BeautifulSoup(text, convertEntities='html')
    tags = [soup]
    while tags:
        tag = tags.pop()
        tags.extend(tag.findChildren())
        for i, (key, value) in enumerate(tag.attrs):
            if value is None:  # Attribute w/o value, like <foo attr/>
                tag.attrs[i] = (key, key)
    return lxml.objectify.fromstring(str(soup))
