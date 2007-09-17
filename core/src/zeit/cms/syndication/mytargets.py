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

import zeit.cms.syndication.interfaces


class MySyndicationTargets(persistent.Persistent,
                           zope.app.container.contained.Contained):

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IMySyndicationTargets)
    zope.component.adapts(zeit.cms.workingcopy.interfaces.IWorkingcopy)

    _targets = ()
    targets = zeit.cms.content.property.KeyReferenceTuple('_targets')


targetFactory = zope.annotation.factory(MySyndicationTargets)
