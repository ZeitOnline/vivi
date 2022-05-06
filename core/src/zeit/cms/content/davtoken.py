import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zope.component
import zope.interface


@zope.component.adapter(bool)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVToken)
def fromBool(value):
    if value:
        return 'yes'
    return 'no'


@zope.component.adapter(type(None))
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVToken)
def fromNone(value):
    # XXX: i'm not sure this is right
    return ''


@zope.component.adapter(str)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVToken)
def fromUnicode(value):
    return value


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVToken)
def fromCMSContent(value):
    return value.uniqueId
