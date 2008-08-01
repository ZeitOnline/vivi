# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Aggregate figures from yesterday with the days before."""

import logging

import gocept.runner
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


def update_lifetime_counters():
    storage = zope.component.getUtility(zeit.today.interfaces.ICountStorage,
                                        name='yesterday')
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)

    for unique_id in storage:
        __traceback_info__ = (unique_id,)
        try:
            content = repository.getContent(unique_id)
        except (KeyError, ValueError):
            log.error("Could not find %s" % unique_id)
            continue

        lifetime = zeit.today.interfaces.ILifeTimeCounter(content)
        count_date = storage.get_count_date(unique_id)
        count = storage.get_count(unique_id)

        if (lifetime.last_count is not None
            and lifetime.last_count >= count_date):
            # Already counted
            continue

        lockable = zope.app.locking.interfaces.ILockable(content)
        try:
            lockable.lock()
        except zope.app.locking.interfaces.LockingError:
            log.warning("Could not update %s because it is locked." %
                        unique_id)
            continue

        try:
            if lifetime.first_count is None:
                lifetime.first_count = count_date
                lifetime.total_hits = count
            else:
                lifetime.total_hits += count

            lifetime.last_count = count_date
        finally:
            lockable.unlock()
        log.debug("Updated %s (%s hits)" % (unique_id, lifetime.total_hits))


# XXX the principal should go to product config
@gocept.runner.appmain(ticks=3600, principal='zope.hitimporter')
def main():
    log.info("Updating hit counters.")
    update_lifetime_counters()
    log.info("Finished updating hit counters.")
