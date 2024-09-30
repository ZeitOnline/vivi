"""Module for custom sql alchemy types

Prevents circular import because converter requires these types and the models too
which also require the converter
"""
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy.types as types


class JSONBWithTupleSupport(types.TypeDecorator):
    """Support JSONB for types that use zope.schema.Tuple
    by converting them into lists"""

    impl = JSONB

    def process_bind_param(self, value, dialect):
        if isinstance(value, tuple):
            value = list(value)
            for i, item in enumerate(value):
                if isinstance(item, tuple):
                    value[i] = list(item)
        return value

    def process_result_value(self, value, dialect):
        return value


class TIMESTAMP(TIMESTAMP):
    def __init__(self):
        super().__init__(timezone=True)
