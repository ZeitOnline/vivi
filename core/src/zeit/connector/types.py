"""Module for custom sql alchemy types

Prevents circular import because converter requires these types and the models too
which also require the converter
"""
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy.types as types


class JSONBTuple(types.TypeDecorator):
    """Support JSONB for types that use zope.schema.Tuple
    by converting them into lists"""

    impl = JSONB

    def process_bind_param(self, value, dialect):
        return self._convert_sequence(value, tuple, list)

    def process_result_value(self, value, dialect):
        return self._convert_sequence(value, list, tuple)

    @staticmethod
    def _convert_sequence(value, source, target):
        if not isinstance(value, source):
            return value  # or raise?
        return target(target(x) if isinstance(x, source) else x for x in value)


class TIMESTAMP(TIMESTAMP):
    def __init__(self):
        super().__init__(timezone=True)
