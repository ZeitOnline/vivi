# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component
import zope.interface

import zeit.objectlog.interfaces


class ProcessForDisplay(object):

    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(zeit.objectlog.interfaces.ILogProcessor)

    def __init__(self, context):
        pass

    def __call__(self, entries):
        return tuple(entries)[-20:]
