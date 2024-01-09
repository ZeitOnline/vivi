from datetime import datetime

import grokcore.component as grok
import pytz
import zope.app.locking.interfaces
import zope.interface

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import WRITEABLE_LIVE
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.content.cp.interfaces import ILeadTime, ILeadTimeWorklist
from zeit.edit.interfaces import IElementReferences
import zeit.cms.content.dav
import zeit.content.cp.interfaces


@zope.interface.implementer(zeit.content.cp.interfaces.ILeadTime)
class LeadTime(zeit.cms.content.dav.DAVPropertiesAdapter):
    start = zeit.cms.content.dav.DAVProperty(
        zeit.content.cp.interfaces.ILeadTime['start'],
        zeit.content.cp.interfaces.DAV_NAMESPACE,
        'leadtime_start',
        writeable=WRITEABLE_LIVE,
    )
    end = zeit.cms.content.dav.DAVProperty(
        zeit.content.cp.interfaces.ILeadTime['end'],
        zeit.content.cp.interfaces.DAV_NAMESPACE,
        'leadtime_end',
        writeable=WRITEABLE_LIVE,
    )


@zope.interface.implementer(zeit.content.cp.interfaces.ILeadTimeWorklist)
class LeadTimeWorklist(zeit.cms.content.dav.DAVPropertiesAdapter):
    zeit.cms.content.dav.mapProperties(
        zeit.content.cp.interfaces.ILeadTimeWorklist,
        zeit.content.cp.interfaces.DAV_NAMESPACE,
        ('previous_leader',),
        writeable=WRITEABLE_LIVE,
    )


def find_leader(cp):
    # The CMS does not have a concept for "*the* lead teaser/article", and in
    # fact it simply is the first teaser on the page.
    try:
        return next(IElementReferences(cp))
    except StopIteration:
        return None


@grok.subscribe(
    zeit.content.cp.interfaces.ILeadTimeCP, zeit.cms.workflow.interfaces.IPublishedEvent
)
def update_leadtime(context, event):
    now = datetime.now(pytz.UTC)
    unmark_previous_leader(context, now)
    mark_current_leader(context, now)


def mark_current_leader(cp, now):
    leader = find_leader(cp)
    if leader is None:
        return

    leadtime = ILeadTime(leader)
    if leadtime.start and not leadtime.end:
        return  # already marked, nothing more to do.

    leadtime.start = now
    leadtime.end = None
    ILeadTimeWorklist(cp).previous_leader = leader
    _update_article(leader)


def unmark_previous_leader(cp, now):
    previous = ILeadTimeWorklist(cp).previous_leader
    if previous is None or previous == find_leader(cp):
        return
    ILeadTime(previous).end = now
    ILeadTimeWorklist(cp).previous_leader = None
    _update_article(previous)


def _update_article(article):
    # Ensure the article is unlocked, so cycling it will actually do something.
    lockable = zope.app.locking.interfaces.ILockable(article, None)
    if not lockable:
        return
    if lockable.isLockedOut():
        lockable.breaklock()
    if lockable.ownLock():
        # If we wanted to do an automatic update, we would have to delete the
        # user's workingcopy, losing data, which is unacceptable. Instead, we
        # do nothing, thus the ILeadTime will be written to XML later on, when
        # the user checks in.
        return

    if IPublishInfo(article).published:
        IPublish(article).publish()
    else:
        # This should never actually happen, since a centerpage cannot be
        # published when it contains unpublished content, so this is more for
        # completeness' sake.
        with checked_out(article):
            pass
