"""Module for converting webdav values to and from the postgresql database.

Just temporary until all columns moved and the filesystem converter ceases to
exist.

See ADR 009
"""

from collections.abc import Iterable

import grokcore.component as grok
import sqlalchemy
import sqlalchemy.dialects.postgresql
import zope.interface
import zope.schema

from zeit.connector.interfaces import IConverter
from zeit.connector.types import JSONBChannels, JSONBTuple
import zeit.cms.content.dav


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


class JSONBTupleConverter(DefaultConverter):
    grok.context(JSONBTuple)

    def serialize(self, value):
        return zeit.cms.content.dav.CollectionTextLineProperty._toProperty(
            value, zeit.cms.content.dav.UnicodeProperty(None, None, None)
        )

    def deserialize(self, value) -> tuple:
        return zeit.cms.content.dav.CollectionTextLineProperty._fromProperty(
            value, zeit.cms.content.dav.UnicodeProperty(zope.schema.Text(), None, None), tuple
        )


class ChannelsConverter(DefaultConverter):
    """Converts list of channels seperated by semicolon and subchannels by space."""

    grok.context(JSONBChannels)

    def serialize(self, value: Iterable) -> str:
        if value is None:
            return None
        return ';'.join(' '.join(x for x in item if x) for item in value)

    def deserialize(self, value: str) -> tuple:
        if not value:
            return ()
        result = []
        for channel in value.split(';'):
            subchannels = channel.split()
            if len(subchannels) > 1:
                result.append(tuple(subchannels))
            else:
                result.append((subchannels[0], None))
        return tuple(result)


class ArrayConverter(DefaultConverter):
    grok.context(sqlalchemy.dialects.postgresql.ARRAY)

    def serialize(self, value):
        return zeit.cms.content.dav.CollectionTextLineProperty._toProperty(
            value, zeit.cms.content.dav.UnicodeProperty(None, None, None)
        )

    def deserialize(self, value):
        return zeit.cms.content.dav.CollectionTextLineProperty._fromProperty(
            value, zeit.cms.content.dav.UnicodeProperty(zope.schema.Text(), None, None), tuple
        )
