# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent

import zope.annotation
import zope.component
import zope.interface
import zope.location

import zeit.cms.settings.interfaces


class GlobalSettings(persistent.Persistent):

    zope.interface.implements(zeit.cms.settings.interfaces.IGlobalSettings)
    zope.component.adapts(zope.location.interfaces.ISite)

    default_year = 2008
    default_volume = 26


global_settings = zope.annotation.factory(GlobalSettings)


@zope.interface.implementer(zeit.cms.settings.interfaces.IGlobalSettings)
@zope.component.adapter(zope.location.interfaces.ILocation)
def parent_settings(context):
    return zeit.cms.settings.interfaces.IGlobalSettings(context.__parent__,
                                                        None)
