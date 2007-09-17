# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

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
