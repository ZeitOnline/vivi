# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component
import zope.interface

import zc.sourcefactory.interfaces

import zeit.cms.interfaces


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromCMSContent(value):
    return value.uniqueId
