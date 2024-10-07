"""Module for converting webdav values to and from the postgresql database.

Just temporary until all columns moved and the filesystem converter ceases to
exist.

See ADR 009
"""
import grokcore.component as grok
import sqlalchemy
import zope.interface

import zeit.cms.content.dav


class IConverter(zope.interface.Interface):
    """Converts webdav values to and from the postgresql database."""

    def serialize(value):
        pass

    def deserialize(value):
        pass


@grok.implementer(IConverter)
@grok.adapter(sqlalchemy.Column)
def converter_from_column_type(column):
    return IConverter(column.type)


@grok.implementer(IConverter)
class DefaultConverter(grok.Adapter):
    grok.context(zope.interface.Interface)

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class BoolConverter(DefaultConverter):
    grok.context(sqlalchemy.Boolean)

    def serialize(self, value):
        return zeit.cms.content.dav.BoolProperty._toProperty(value)

    def deserialize(self, value):
        return zeit.cms.content.dav.BoolProperty._fromProperty(value)


class IntConverter(DefaultConverter):
    grok.context(sqlalchemy.Integer)

    def serialize(self, value):
        return str(value)

    def deserialize(self, value):
        return int(value)


class DatetimeConverter(DefaultConverter):
    grok.context(sqlalchemy.TIMESTAMP)

    def serialize(self, value):
        return zeit.cms.content.dav.DatetimeProperty._toProperty(value)

    def deserialize(self, value):
        return zeit.cms.content.dav.DatetimeProperty._fromProperty(value)
