from sqlalchemy import cast
from sqlalchemy_utils import Ltree, LtreeType
from sqlalchemy_utils.types.ltree import LQUERY

from zeit.connector.interfaces import ID_NAMESPACE


class ltree(Ltree):
    def __init__(self, value):
        if value.startswith(ID_NAMESPACE):
            value = value.replace(ID_NAMESPACE, '', 1)
            value = self._escape(value)
            value = value.replace('/', '.')
        super().__init__(value)

    @staticmethod
    def _escape(value):
        return value.replace('.', '__dot__')

    @staticmethod
    def _unescape(value):
        return value.replace('__dot__', '.')

    def to_uniqueid(self):
        return ID_NAMESPACE + '/'.join([self._unescape(x) for x in self.path.split('.')])


def coerce_with_our_value_class(self, value):
    if value:
        return ltree(value)


LtreeType._coerce = coerce_with_our_value_class


def lquery_with_cast(self, other):  # That upstream omits this seems like a bug
    if not isinstance(other, list):
        other = cast(other, LQUERY)
    return orig_lquery(self, other)


orig_lquery = LtreeType.comparator_factory.lquery
LtreeType.comparator_factory.lquery = lquery_with_cast
