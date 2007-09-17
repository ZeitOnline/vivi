# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent
import transaction
import BTrees.OOBTree
import ZODB.blob

import zope.annotation.factory
import zope.location.interfaces

import zeit.connector.interfaces


class TransactionBoundCache(object):

    # XXX move to seperate package for reuse.

    def __init__(self, name, factory):
        self.attribute = name
        self.factory = factory

    def __get__(self, instance, class_):
        try:
            cache = getattr(instance, self.attribute)
        except AttributeError:
            cache = self.factory()
            setattr(instance, self.attribute, cache)
            transaction.get().addBeforeCommitHook(
                self.invalidate, (instance, ))
        return cache

    def invalidate(self, instance):
        try:
            delattr(instance, self.attribute)
        except AttributeError:
            pass


class ResourceCache(persistent.Persistent):
    """Cache for ressource data."""

    zope.interface.implements(zeit.connector.interfaces.IResourceCache)
    zope.component.adapts(zope.location.interfaces.ISite)

    properties = TransactionBoundCache('_v_properties', dict)
    child_ids = TransactionBoundCache('_v_childnames', dict)

    def __init__(self):
        self._etags = BTrees.OOBTree.OOBTree()
        self._data = BTrees.OOBTree.OOBTree()
        self.locktokens = BTrees.OOBTree.OOBTree()

    def getData(self, unique_id, properties):
        current_etag = properties[('getetag', 'DAV:')]
        cached_etag = self._etags.get(unique_id)

        if current_etag != cached_etag:
            raise KeyError("Object %r is not cached." % unique_id)
        return self._data[unique_id].open('r')

    def setData(self, unique_id, properties, data):
        current_etag = properties.get(('getetag', 'DAV:'))
        if current_etag is None:
            # When we have no etag, we must not store the data as we have no
            # means of invalidation then.
            return
        blob = ZODB.blob.Blob()
        blob_file = blob.open('w')
        buffer_size = 102400
        if hasattr(data, 'seek'):
            data.seek(0)
        while True:
            s = data.read(buffer_size)
            blob_file.write(s)
            if len(s) < buffer_size:
                break
        blob_file.close()
        self._etags[unique_id] = current_etag
        self._data[unique_id] = blob
        transaction.savepoint(optimistic=True)
        return blob.open('r')


resourceCacheFactory = zope.annotation.factory(ResourceCache)
