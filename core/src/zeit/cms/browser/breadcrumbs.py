# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tree.py 9072 2007-09-24 15:37:05Z zagy $

import zope.traversing.api
import zope.component
import zope.cachedescriptors.property

import zeit.cms.repository.interfaces


class Breadcrumbs(object):

    @zope.cachedescriptors.property.Lazy
    def get_breadcrumbs(self):
        """Returns a list of dicts with title and URL."""
        result = []
        traverse_items = [self.context]
        traverse_items += zope.traversing.api.getParents(self.context)

        for item in traverse_items:
            url = zope.component.getMultiAdapter(
                (item, self.request), name="absolute_url")()
            title = item.__name__
            result.append(dict(title=title, url=url))
            if zeit.cms.repository.interfaces.IRepository.providedBy(item):
                break
        result.reverse()
        return result
