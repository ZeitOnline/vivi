import string

import persistent
import zope.annotation
import zope.component
import zope.interface
import zope.location

import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.settings.interfaces


@zope.component.adapter(zope.location.interfaces.ISite)
@zope.interface.implementer(zeit.cms.settings.interfaces.IGlobalSettings)
class GlobalSettings(persistent.Persistent):
    default_year = 2008
    default_volume = 26

    def get_working_directory(self, template, **additional_replacements):
        path = string.Template(template).substitute(
            dict(year=self.default_year, volume=self.default_volume, **additional_replacements)
        )
        path = path.split('/')

        target_folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/')
        for next_name in path:
            if not next_name:
                continue
            if next_name not in target_folder:
                target_folder[next_name] = zeit.cms.repository.folder.Folder()
            target_folder = target_folder[next_name]
        return target_folder


global_settings = zope.annotation.factory(GlobalSettings)


@zope.interface.implementer(zeit.cms.settings.interfaces.IGlobalSettings)
@zope.component.adapter(zope.location.interfaces.ILocation)
def parent_settings(context):
    return zeit.cms.settings.interfaces.IGlobalSettings(context.__parent__, None)
