# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.cms.repository.interfaces
import zope.component


class Sidebar(zeit.cms.browser.view.Base):

    def tree_url(self):
        return self.url(self.repository, '@@zeit.cms.sitecontrol.tree')

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @property
    def index_url(self):
        if 'index' in self.repository:
            return self.url(self.repository['index'], '@@index')
        return self.url(self.repository)
