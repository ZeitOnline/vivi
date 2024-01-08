import zc.sourcefactory.interfaces
import zope.component
import zope.interface

import zeit.cms.interfaces


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromCMSContent(value):
    return value.uniqueId
