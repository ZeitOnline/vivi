from sqlalchemy.dialects.postgresql import JSONB
import grokcore.component as grok
import sqlalchemy
import zope.interface

import zeit.connector.interfaces


@grok.implementer(zeit.connector.interfaces.IConverter)
@grok.adapter(sqlalchemy.Column)
def converter_from_column_type(column):
    return zeit.connector.interfaces.IConverter(column.type)


@grok.implementer(zeit.connector.interfaces.IConverter)
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


@grok.implementer(zeit.connector.interfaces.IConverter)
class DictConverter(grok.Adapter):
    grok.context(JSONB)

    def serialize(self, value):
        if not value:
            return {}
        return value

    def deserialize(self, value):
        if not value:
            return {}
        return value
