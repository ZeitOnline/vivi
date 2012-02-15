# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zope.cachedescriptors.property
import zope.location.interfaces
import zope.traversing.api


class Breadcrumbs(zeit.cms.browser.view.Base):

    @zope.cachedescriptors.property.Lazy
    def get_breadcrumbs(self):
        """Returns a list of dicts with title and URL."""
        result = []
        traverse_items = [self.context]
        traverse_items += zope.traversing.api.getParents(self.context)

        for item in traverse_items:
            if zope.location.interfaces.ISite.providedBy(item):
                break
            title = item.__name__
            uniqueId = getattr(item, 'uniqueId', None)
            result.append(
                dict(title=title,
                     url=self.url(item),
                     uniqueId=uniqueId))

        result.reverse()
        return result
