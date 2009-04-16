# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.settings.interfaces
import zope.annotation
import zope.component
import zope.interface
import zope.location


class GlobalSettings(persistent.Persistent):

    zope.interface.implements(zeit.cms.settings.interfaces.IGlobalSettings)
    zope.component.adapts(zope.location.interfaces.ISite)

    default_year = 2008
    default_volume = 26

    def get_online_working_directory(self):
        target_folder = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/')
        for next_name in ('online', str(self.default_year),
                          str(self.default_volume)):
            if next_name not in target_folder:
                target_folder[next_name] = zeit.cms.repository.folder.Folder()
            target_folder = target_folder[next_name]
        return target_folder


global_settings = zope.annotation.factory(GlobalSettings)


@zope.interface.implementer(zeit.cms.settings.interfaces.IGlobalSettings)
@zope.component.adapter(zope.location.interfaces.ILocation)
def parent_settings(context):
    return zeit.cms.settings.interfaces.IGlobalSettings(context.__parent__,
                                                        None)
