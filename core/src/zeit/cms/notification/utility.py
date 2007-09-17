# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zc.notification.notification

import zeit.cms.notification.notifier


def notificationUtilityFactory():
    utility = zc.notification.notification.NotificationUtility()
    return utility
