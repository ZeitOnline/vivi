# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.cms.repository.interfaces
import zope.component


class Sidebar(zeit.cms.browser.view.Base):

    def tree_url(self):
        view = zope.component.getMultiAdapter(
            (self.repository, self.request), name='zeit.cms.sitecontrol.tree')
        return self.url(view)

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @property
    def index_url(self):
        if 'index' not in self.repository:
            return '#'
        view = zope.component.getMultiAdapter(
            (self.repository['index'], self.request), name='checkout')
        return self.url(view)
