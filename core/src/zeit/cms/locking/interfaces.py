# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.schema
import zope.app.locking.interfaces


class ILockInfo(zope.app.locking.interfaces.ILockInfo):
    """Extended LockInfo interface."""

    locked_until = zope.schema.Datetime(
        title=u"Locked Until",
        required=False)
