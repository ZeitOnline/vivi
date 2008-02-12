# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface
import zope.schema

import zope.app.security.interfaces

import zeit.cms.content.interfaces


class ChoicePropertyWithPrincipalSource(object):

    zope.component.adapts(
        zope.schema.interfaces.IChoice,
        zope.app.security.interfaces.IPrincipalSource)
    zope.interface.implements(
        zeit.cms.content.interfaces.IDAVPropertyConverter)

    def __init__(self, context, source):
        self.context = context
        self.source = source

    def fromProperty(self, value):
        source = zope.app.security.vocabulary.PrincipalSource()
        if value in source:
            return value

    def toProperty(self, value):
        return value

