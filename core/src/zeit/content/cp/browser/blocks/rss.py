# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.checkout.helper
import zeit.cms.content
import zeit.content.cp.browser.blocks.av
import zeit.content.cp.browser.view
import zeit.content.cp.interfaces
import zope.formlib.form
import zope.security.proxy


class Refresh(zeit.content.cp.browser.view.Action):

    def update(self):
        fm = zope.component.getUtility(zeit.content.cp.interfaces.IFeedManager)
        fm.refresh_feed(self.context.url)
        self.signal(None, 'reload',
                    self.context.__name__, self.url(self.context, 'contents'))


class EditProperties(zeit.content.cp.browser.blocks.av.EditProperties):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IRSSBlock).select('url')
