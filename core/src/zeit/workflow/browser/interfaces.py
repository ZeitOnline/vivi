# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.i18nmessageid
import zope.interface
import zope.schema


_ = zope.i18nmessageid.MessageFactory('zeit.cms')


class ILockFormSchema(zope.interface.Interface):

    locked = zope.schema.Bool(
        title=_('Locked'))

    locker = zope.schema.TextLine(
        title=_('Locker'),
        required=False)

    locked_until = zope.schema.Datetime(
        title=_('Locked until'),
        required=False)
