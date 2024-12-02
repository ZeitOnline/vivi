import contextlib
import logging

import zeit.cms.checkout.interfaces


log = logging.getLogger(__name__)


def with_checked_out(content, function, events=True):
    """Call a function with a checked out version of content.

    Function makes sure content is checked back in after the function ran.

    """
    with checked_out(content, events) as checked_out_obj:
        if checked_out_obj is not None:
            changed = function(checked_out_obj)
            if not changed:
                raise zeit.cms.checkout.interfaces.NotChanged()


@contextlib.contextmanager
def checked_out(
    content,
    events=True,
    semantic_change=None,
    ignore_conflicts=False,
    temporary=True,
    raise_if_error=False,
    will_publish_soon=False,
):
    __traceback_info__ = (content.uniqueId,)
    manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
    try:
        checked_out = manager.checkout(temporary=temporary, event=events)
    except zeit.cms.checkout.interfaces.CheckinCheckoutError as err:
        if raise_if_error:
            raise err
        else:
            log.warning('Could not checkout %s.' % content.uniqueId, exc_info=True)
            yield None
    else:
        try:
            yield checked_out
        except zeit.cms.checkout.interfaces.NotChanged:
            del checked_out.__parent__[checked_out.__name__]
        else:
            manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
            manager.checkin(
                event=events,
                semantic_change=semantic_change,
                ignore_conflicts=ignore_conflicts,
                will_publish_soon=will_publish_soon,
            )
