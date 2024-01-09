import collections

import zc.sourcefactory.basic
import zope.component
import zope.interface
import zope.security.checker

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces


class _NotNecessary:
    __slots__ = ()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __repr__(self):
        return 'NotNecessary'

    def __reduce__(self):
        return (_NotNecessary, ())


NotNecessary = _NotNecessary()
# Make it a rock
zope.security.checker.BasicTypes[_NotNecessary] = zope.security.checker.NoProxy


@zope.component.adapter(_NotNecessary)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVToken)
def fromNotNecessary(value):
    return 'notnecessary'


class TriState(zc.sourcefactory.basic.BasicSourceFactory):
    """Source providing yes/no/notnecessary."""

    _values = collections.OrderedDict(
        (
            (False, _('no')),
            (True, _('yes')),
            (NotNecessary, _('not necessary')),
        )
    )

    def getTitle(self, value):
        return self._values.get(value, value)

    def getValues(self):
        return self._values.keys()
