import BTrees
import persistent
import zope.annotation
import zope.component
import zope.container.contained
import zope.interface

import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces


@zope.component.adapter(zeit.cms.workingcopy.interfaces.IWorkingcopy)
@zope.interface.implementer(zeit.cms.repository.interfaces.IUserPreferences)
class UserPreferences(persistent.Persistent, zope.container.contained.Contained):
    default_shown_containers = (
        'http://xml.zeit.de/repository/2007',
        'http://xml.zeit.de/repository/2008',
        'http://xml.zeit.de/repository/bilder',
        'http://xml.zeit.de/repository/bilder/2007',
        'http://xml.zeit.de/repository/bilder/2008',
        'http://xml.zeit.de/repository/hp_channels',
        'http://xml.zeit.de/repository/online',
        'http://xml.zeit.de/repository/online/2007',
        'http://xml.zeit.de/repository/online/2008',
        'http://xml.zeit.de/repository/themen',
    )

    def __init__(self):
        self._hidden_containers = BTrees.family32.OI.TreeSet()
        self._set_default_hidden_containers()

    def hide_container(self, container):
        self._hidden_containers.insert(container.uniqueId)

    def show_container(self, container):
        try:
            self._hidden_containers.remove(container.uniqueId)
        except KeyError:
            pass

    def is_hidden(self, container):
        return container.uniqueId in self._hidden_containers

    def get_hidden_containers(self):
        return self._hidden_containers

    def _set_default_hidden_containers(self):
        hidden = set()
        shown = set()
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        for unique_id in self.default_shown_containers:
            try:
                container = repository.getContent(unique_id)
            except KeyError:
                # When the container doesn't exist any more we just ignore it.
                continue
            hidden.update(container.__parent__.values())
            shown.add(container)

        for container in hidden.difference(shown):
            self.hide_container(container)


preferenceFactory = zope.annotation.factory(UserPreferences)
