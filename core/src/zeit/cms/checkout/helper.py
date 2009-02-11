# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import logging
import z3c.flashmessage.interfaces
import zope.component

import zeit.cms.checkout.interfaces
from zeit.cms.i18n import MessageFactory as _

log = logging.getLogger(__name__)


def with_checked_out(content, function, events=True):
    """Call a function with a checked out version of content.

    Function makes sure content is checked back in after the function ran.

    """
    __traceback_info__ = (content.uniqueId,)
    manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
    try:
        checked_out = manager.checkout(temporary=True, event=events)
    except zeit.cms.checkout.interfaces.CheckinCheckoutError, e:
        log.warning("Could not checkout %s for related update." %
                       content.uniqueId)
        log.exception(e)
        return

    changed = function(checked_out)

    if changed:
        manager = zeit.cms.checkout.interfaces.ICheckinManager(
            checked_out)
        manager.checkin(event=events)
    else:
        del checked_out.__parent__[checked_out.__name__]
