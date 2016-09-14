import unicodedata
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zope.cachedescriptors.property
import zope.interface


class Tag(object):
    """Representation of a keyword."""

    zope.interface.implements(zeit.cms.tagging.interfaces.ITag,
                              zeit.cms.interfaces.ICMSContent)

    SEPARATOR = u':=)'

    def __init__(self, label, entity_type):
        self.label = label
        self.entity_type = entity_type
        self.pinned = False  # pinned state is set from outside after init

    @zope.cachedescriptors.property.Lazy
    def code(self):
        return u''.join((self.entity_type, self.SEPARATOR, self.label))

    @zope.cachedescriptors.property.Lazy
    def url_value(self):
        return unicodedata.normalize(
            'NFKD', self.label).encode('ascii', 'ignore').lower()

    @classmethod
    def from_code(cls, code):
        if cls.SEPARATOR not in code:
            return None
        entity_type, sep, label = code.partition(cls.SEPARATOR)
        return cls(label, entity_type)

    def __eq__(self, other):
        # XXX this is not a generic equality check. From a domain perspective,
        # two tags are the same when their codes are the same. However, since
        # we want to edit ``pinned``, and formlib compares the *list* of
        # keywords, which uses == on the items, we need to include pinned here.
        if not zeit.cms.tagging.interfaces.ITag.providedBy(other):
            return False
        return self.code == other.code and self.pinned == other.pinned

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def uniqueId(self):
        return (zeit.cms.tagging.interfaces.ID_NAMESPACE +
                self.code.encode('unicode_escape'))
