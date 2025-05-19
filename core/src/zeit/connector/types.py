"""Module for custom sql alchemy types

Prevents circular import because converter requires these types and the models too
which also require the converter
"""

from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
import sqlalchemy.types as types


class TupleTypeDecorator(types.TypeDecorator):
    """Support python-side zope.schema.Tuple by converting them into list for
    sqlalchemy processing.
    """

    impl = NotImplemented
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return self._convert_sequence(value, tuple, list)

    def process_result_value(self, value, dialect):
        return self._convert_sequence(value, list, tuple)

    @staticmethod
    def _convert_sequence(value, source, target):
        if not isinstance(value, source):
            return value  # or raise?
        return target(target(x) if isinstance(x, source) else x for x in value)

    def coerce_compared_value(self, op, value):
        return self.impl.coerce_compared_value(op, value)


class JSONBTuple(TupleTypeDecorator):
    impl = JSONB


class JSONBChannels(JSONBTuple):
    """Subclass so we can register a specific DAV converter for it."""


class ArrayTuple(TupleTypeDecorator):
    impl = ARRAY


class TIMESTAMP(TIMESTAMP):
    def __init__(self):
        super().__init__(timezone=True)
