# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zc.sourcefactory.interfaces

import zeit.workflow.source


@zope.component.adapter(zeit.workflow.source._NotNeeded)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromNotNeeded(value):
    return 'NotNeeded'
