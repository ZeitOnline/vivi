# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Aggregate figures from yesterday with the days before."""

import logging

import gocept.runner
import zc.queue
import zope.annotation.interfaces
import zope.app.appsetup.product
import zope.app.locking.interfaces
import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.content.dav
import zeit.today.interfaces
import zeit.today.storage


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.today.interfaces.ICountStorage)
def yesterday_storage_factory():
    def url_getter():
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.today')
        return config['yesterday-xml-url']
    return zeit.today.storage.CountStorage(url_getter)



class LifeTimeCounter(object):

    zope.interface.implements(zeit.today.interfaces.ILifeTimeCounter)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    zeit.cms.content.dav.mapProperties(
        zeit.today.interfaces.ILifeTimeCounter,
        zeit.today.interfaces.LIFETIME_DAV_NAMESPACE,
        ('total_hits', 'first_count', 'last_count'),
        live=True)

    def __init__(self, context):
        self.context = context


@zope.component.adapter(LifeTimeCounter)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def webdav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)


class UpdateLifetimecounters(object):

    TICKS = 0.025

    def __call__(self):
        ticks = self.TICKS
        if self.queue:
            self.process_one()
            if not self.queue:
                ticks = None
        else:
            self.fill_queue()

        return ticks

    def process_one(self):
        unique_id, count_date, count = self.queue.pull()
        __traceback_info__ = (unique_id,)
        try:
            content = self.repository.getContent(unique_id)
        except (KeyError, ValueError):
            log.warning("Could not find %s" % unique_id)
            return

        lockable = zope.app.locking.interfaces.ILockable(content)
        try:
            lockable.lock(timeout=10)
        except zope.app.locking.interfaces.LockingError:
            log.warning("Could not update %s because it is locked." %
                        unique_id)
            return

        try:
            lifetime = zeit.today.interfaces.ILifeTimeCounter(content)

            if (lifetime.last_count is not None
                and lifetime.last_count >= count_date):
                # Already counted
                return
            if lifetime.first_count is None:
                lifetime.first_count = count_date
                lifetime.total_hits = count
            else:
                lifetime.total_hits += count

            lifetime.last_count = count_date
        finally:
            lockable.unlock()
        log.debug("Updated %s (%s hits)" % (unique_id, lifetime.total_hits))

    def fill_queue(self):
        for unique_id in self.storage:
            count_date = self.storage.get_count_date(unique_id)
            count = self.storage.get_count(unique_id)
            self.queue.put((unique_id, count_date, count))

    @zope.cachedescriptors.property.Lazy
    def storage(self):
        return zope.component.getUtility(zeit.today.interfaces.ICountStorage,
                                         name='yesterday')
    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @zope.cachedescriptors.property.Lazy
    def queue(self):
        site = zope.app.component.hooks.getSite()
        annotations = zope.annotation.interfaces.IAnnotations(site)
        try:
            queue = annotations[__name__]
        except KeyError:
            queue = annotations[__name__] = zc.queue.CompositeQueue()
        return queue


def update_lifetime_counters():
    ticks = UpdateLifetimecounters()()
    return ticks


# XXX the principal should go to product config
@gocept.runner.appmain(ticks=3600, principal='zope.hitimporter')
def main():
    return update_lifetime_counters()
