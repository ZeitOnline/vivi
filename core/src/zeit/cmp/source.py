import grokcore.component as grok
import zc.sourcefactory.basic
import zc.sourcefactory.interfaces
import zope.component
import zope.interface
import zope.security.checker

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces


# Copy&paste from zeit.workflow.source for the yes/no/other tri-state mechanics


class UnknownType:
    __slots__ = ()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __repr__(self):
        return 'Unknown'

    def __reduce__(self):
        return (UnknownType, ())


Unknown = UnknownType()
zope.security.checker.BasicTypes[UnknownType] = zope.security.checker.NoProxy


@grok.adapter(UnknownType)
@grok.implementer(zeit.cms.content.interfaces.IDAVToken)
def dav_token(value):
    return 'unknown'


@grok.adapter(UnknownType)
@grok.implementer(zc.sourcefactory.interfaces.IToken)
def source_token(value):
    return 'unknown'


class TriState(zc.sourcefactory.basic.BasicSourceFactory):
    _values = {True: _('yes'), False: _('no'), Unknown: _('unknown')}

    def getTitle(self, value):
        return self._values.get(value, value)

    def getValues(self):
        return self._values.keys()
