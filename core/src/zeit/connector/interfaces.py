# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface


class DeleteProperty(object):
    """Singleton to indicate a property should be deleted."""

    def __repr__(self):
        return 'DeleteProperty'


DeleteProperty = DeleteProperty()


class IResourceCache(zope.interface.Interface):
    """A cache for resource data."""

    def getData(unique_id, dav_resource):
        """Return data for given unique_id and dav_resource.

        The data will cached before it is returned. If the data is cached it
        will be returned from the cache.

        The cache will be automatically invalidated if the etag of the resouce
        changes.

        """
