=============
Notifications
=============


We need to set the site since we're a functional test::

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())


Login bob::

    >>> import zope.security.management
    >>> import zope.security.testing
    >>> zope.security.management.endInteraction()
    >>> principal = zope.security.testing.Principal('bob')
    >>> participation = zope.security.testing.Participation(principal)
    >>> zope.security.management.newInteraction(participation)

Get the utility::

    >>> import zope.component
    >>> import zc.notification.interfaces
    >>> notify_utility = zope.component.getUtility(
    ...     zc.notification.interfaces.INotificationUtility)

Register bob for the `test-notification`::

    >>> notify_utility.setRegistrations('bob', ['test-notification'])

Create a notification for `bob`::

    >>> from zc.notification.notification import PrincipalNotification
    >>> notification = PrincipalNotification(
    ...     'test-notification', 'Notification-Message', ('bob',),
    ...     summary="short")
    >>> notify_utility.notify(notification)

Check that bob actually received the notification::

    >>> import zeit.cms.notification.interfaces
    >>> principal.id
    'bob'
    >>> bobs_notifications = (
    ...    zeit.cms.notification.interfaces.IPrincipalNotifications(principal))
    >>> bobs_notifications
    <zeit.cms.notification.notifier.PrincipalNotifications object at 0x...>
    >>> list(bobs_notifications)
    [<zc.notification.notification.PrincipalNotification object at 0x...>]


Log bob out again::

    >>> zope.security.management.endInteraction()

Cleanup
=======

After tests we clean up::

    >>> zope.app.component.hooks.setSite(old_site)
