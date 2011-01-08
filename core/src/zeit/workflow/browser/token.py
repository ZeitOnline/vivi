# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zc.sourcefactory.interfaces

import zeit.workflow.source


@zope.component.adapter(zeit.workflow.source._NotNecessary)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromNotNecessary(value):
    return 'NotNecessary'
