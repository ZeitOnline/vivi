# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.blocks.av
import zeit.content.cp.interfaces
import zope.formlib.form

class EditProperties(zeit.content.cp.browser.blocks.av.EditProperties):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IRSSBlock)
