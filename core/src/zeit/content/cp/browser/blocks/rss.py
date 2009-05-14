# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.blocks.av
import zeit.content.cp.interfaces
import zope.formlib.form
import zope.security.proxy
import zeit.cms.content
import zeit.cms.checkout.helper


class Refresh(object):

    def __call__(self):
        fm = zope.component.getUtility(zeit.content.cp.interfaces.IFeedManager)
        fm.refresh_feed(self.context.url)


class EditProperties(zeit.content.cp.browser.blocks.av.EditProperties):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IRSSBlock).select('url')
