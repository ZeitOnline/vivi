# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import types

import zope.component
import zope.interface

import zeit.cms.content.interfaces


@zope.component.adapter(bool)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVToken)
def fromBool(value):
    if value:
        return 'yes'
    return 'no'


@zope.component.adapter(types.NoneType)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVToken)
def fromNone(value):
    # XXX: i'm not sure this is right
    return ''


@zope.component.adapter(unicode)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVToken)
def fromUnicode(value):
    return value
