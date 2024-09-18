import datetime

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

    def serialize(self, value: bool) -> str:
        return zeit.cms.content.dav.BoolProperty._toProperty(value)

    def deserialize(self, value: str) -> bool:
        return zeit.cms.content.dav.BoolProperty._fromProperty(value)


class IntConverter(DefaultConverter):
    grok.context(sqlalchemy.Integer)

    def serialize(self, value: int) -> str:
        return str(value)

    def deserialize(self, value: str) -> int:
        return int(value)


class DatetimeConverter(DefaultConverter):
    grok.context(sqlalchemy.TIMESTAMP)

    def serialize(self, value: datetime.datetime) -> str:
        return zeit.cms.content.dav.DatetimeProperty._toProperty(value)

    def deserialize(self, value: str) -> datetime.datetime:
        return zeit.cms.content.dav.DatetimeProperty._fromProperty(value)


class ChannelsConverter(DefaultConverter):
    grok.context(JSONB)
    grok.name('channels')

    def serialize(self, value: dict) -> str:
        if not value:
            return ''
        elements = []
        for channel, subchannels in value.items():
            if subchannels:
                elements.append(f"{channel} {' '.join(subchannels)}")
            else:
                elements.append(channel)
        return ';'.join(elements)

    def deserialize(self, value: str) -> dict:
        """channels are separated by semicolon, subchannels are separated by space"""
        channels = {}
        if value:
            elements = [i.split() for i in value.split(';') if i.strip()]
            for element in elements:
                channel = element[0]
                subchannels = element[1:] if len(element) > 1 else []
                if channel in channels:
                    channels[channel].extend(subchannels)
                else:
                    channels[channel] = subchannels
        return channels
