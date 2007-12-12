# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zc.set

import persistent

import zope.annotation
import zope.component
import zope.interface

import zope.app.container.contained

import zeit.cms.interfaces
import zeit.cms.content.property
import zeit.cms.workingcopy.interfaces

import zeit.cms.repository.interfaces


class UserPreferences(persistent.Persistent,
                      zope.app.container.contained.Contained):

    zope.interface.implements(
        zeit.cms.repository.interfaces.IUserPreferences)
    zope.component.adapts(zeit.cms.workingcopy.interfaces.IWorkingcopy)

    _hidden_containers = zc.set.Set()

    default_shown_containers = (
        'http://xml.zeit.de/online',
        'http://xml.zeit.de/online/2007',
        'http://xml.zeit.de/2007',
        'http://xml.zeit.de/bilder',
        'http://xml.zeit.de/bilder/2007',
        'http://xml.zeit.de/deutschland',
        'http://xml.zeit.de/hp_channels',
        'http://xml.zeit.de/international',
        'http://xml.zeit.de/kultur',
        'http://xml.zeit.de/leben',
        'http://xml.zeit.de/themen',
        'http://xml.zeit.de/wirtschaft',
        'http://xml.zeit.de/wissen',
    )

    def __init__(self):
        self._set_default_hidden_containers()

    def hide_container(self, container):
        self._hidden_containers.add(container.uniqueId)

    def show_container(self, container):
        try:
            self._hidden_containers.remove(container.uniqueId)
        except KeyError:
            pass

    def is_hidden(self, container):
        return container.uniqueId in self._hidden_containers

    def _set_default_hidden_containers(self):
        hidden = set()
        shown = set()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
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
