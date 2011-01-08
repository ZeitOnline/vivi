# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.traversing.api
import zope.component
import zope.cachedescriptors.property
import zope.location.interfaces


class Breadcrumbs(object):

    @zope.cachedescriptors.property.Lazy
    def get_breadcrumbs(self):
        """Returns a list of dicts with title and URL."""
        result = []
        traverse_items = [self.context]
        traverse_items += zope.traversing.api.getParents(self.context)

        for item in traverse_items:
            if zope.location.interfaces.ISite.providedBy(item):
                break
            url = zope.component.getMultiAdapter(
                (item, self.request), name="absolute_url")()
            title = item.__name__
            uniqueId = getattr(item, 'uniqueId', None)
            result.append(
                dict(title=title,
                     url=url,
                     uniqueId=uniqueId))

        result.reverse()
        return result
