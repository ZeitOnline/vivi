# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.blocks.av
import zeit.content.cp.interfaces
import zope.formlib.form
import zope.security.proxy

class Display(object):

    def css_class(self):
        if self.error():
            return 'validation-error'
        return ''

    def error(self):
        feed = zope.security.proxy.removeSecurityProxy(self.context.feed)
        return feed.xml.get('error')


class EditProperties(zeit.content.cp.browser.blocks.av.EditProperties):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IRSSBlock).select('url')
