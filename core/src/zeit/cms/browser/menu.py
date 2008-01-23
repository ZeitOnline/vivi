# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.publisher.browser.menu

import z3c.menu.simple.menu


class ExternalActionsMenu(zope.app.publisher.browser.menu.BrowserMenu):

    def getMenuItems(self, object, request):
        result = super(ExternalActionsMenu, self).getMenuItems(object, request)
        for item in result:
            item['target'] = "_blank"
        return result


class GlobalMenuItem(z3c.menu.simple.menu.GlobalMenuItem):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'globalmenuitem.pt')

    activeCSS = 'selected'
    inActiveCSS = ''
    pathitem = ''

    @property
    def selected(self):
        app_url = self.request.getApplicationURL()
        url = self.request.getURL()
        path = url[len(app_url):].split('/')
        if path and self.pathitem in path:
            return True

        return False
