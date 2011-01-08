# Copyright (c) 2006-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
import zope.viewlet.manager

class SortingViewletManager(zope.viewlet.manager.ViewletManagerBase):

    def sort(self, viewlets):
        return sorted(viewlets)
