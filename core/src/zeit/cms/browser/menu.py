# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.publisher.browser.menu


class ExternalActionsMenu(zope.app.publisher.browser.menu.BrowserMenu):

    def getMenuItems(self, object, request):
        result = super(ExternalActionsMenu, self).getMenuItems(object, request)
        for item in result:
            item['target'] = "_blank"
        return result
