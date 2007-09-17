# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.annotation
import zope.component
import zope.interface
import zope.security.interfaces

import zope.app.security.interfaces

import zc.notification.interfaces
import zc.set

import zeit.cms.notification.interfaces


class SystemNotifier(object):

    zope.interface.implements(zc.notification.interfaces.INotifier)

    def send(self, notification, principal_id, annotations, context):
        """Store notifications for principal."""
        principalNotificationFactory(annotations).add(notification)


class PrincipalNotifications(object):

    zope.interface.implements(
        zeit.cms.notification.interfaces.IPrincipalNotifications)
    zope.component.adapts(zope.security.interfaces.IPrincipal)

    def __init__(self):
        self._notifications = zc.set.Set()

    def add(self, notification):
        self._notifications.add(notification)

    def __iter__(self):
        return iter(self._notifications)


principalNotificationFactory = zope.annotation.factory(
    PrincipalNotifications)
