# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent

import zope.annotation
import zope.component
import zope.interface

import zope.app.container.contained

import zeit.cms.content.property
import zeit.cms.workingcopy.interfaces

import zeit.cms.repository.interfaces


class UserPreferences(persistent.Persistent,
                      zope.app.container.contained.Contained):

    zope.interface.implements(
        zeit.cms.repository.interfaces.IUserPreferences)
    zope.component.adapts(zeit.cms.workingcopy.interfaces.IWorkingcopy)

    _hidden_containers = ()
    hidden_containers = zeit.cms.content.property.KeyReferenceTuple(
        '_hidden_containers')


preferenceFactory = zope.annotation.factory(UserPreferences)
