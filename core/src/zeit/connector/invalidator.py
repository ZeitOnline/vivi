# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import BTrees
import gocept.runner
import logging
import persistent
import zeit.connector.interfaces
import zope.component
import zope.event
import zope.interface


log = logging.getLogger(__name__)


class IInvalidator(zope.interface.Interface):
    """Invalidate caches."""

    def __call__():
        """Process one step.

        returns True when finished, False otherwise.

        """

class Invalidator(persistent.Persistent):

    def __init__(self):
        self.working_set = BTrees.family32.OI.TreeSet()
        self.missed = BTrees.family32.OI.TreeSet()
        self.got = BTrees.family32.OI.TreeSet()

    def __call__(self):
        if self.working_set:
            self.refresh_one()
        else:
            self.fill_working_set()
        if self.working_set:
            return False
        self.invalidate_missed()
        return True

    def fill_working_set(self):
        log.info("Filling working set.")
        self.working_set.update(self.property_cache.keys())
        self.missed.clear()
        self.got.clear()

    def refresh_one(self):
        collection = self.get_next_collection()
        if collection is None:
            return
        log.info("Refreshing %s" % collection)
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(collection))
        # Reload the folder's metadata (depth=1)
        try:
            resource = self.connector[collection]
        except KeyError:
            pass
        else:
            if resource.contentType == 'httpd/unix-directory':
                self.got.update(
                    o[1] for o in self.connector.listCollection(collection))
            else:
                self.missed.insert(resource.id)

    def get_next_collection(self):
        while self.working_set:
            collection = self.working_set.minKey()
            self.working_set.remove(collection)
            if collection.endswith('/'):
                return collection
            self.missed.insert(collection)

    def invalidate_missed(self):
        log.info("Invalidating deleted objects.")
        really_missed = BTrees.family32.OI.difference(self.missed, self.got)
        property_cache = self.property_cache
        for id in really_missed:
            zope.event.notify(
                zeit.connector.interfaces.ResourceInvaliatedEvent(id))
            try:
                property_cache.remove(id)
            except KeyError:
                pass

    @property
    def connector(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IConnector)

    @property
    def property_cache(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IPropertyCache)


@gocept.runner.appmain(ticks=0.05)
def invalidate_whole_cache():
    invalidator = zope.component.getUtility(IInvalidator)
    finished = invalidator()
    if finished:
        return gocept.runner.Exit
