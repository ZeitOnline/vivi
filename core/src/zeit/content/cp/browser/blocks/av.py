# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.formlib.form
import zeit.content.cp.interfaces
import zeit.content.cp.browser.blocks.block

class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IAVBlock).omit(
            'media_type', *list(zeit.content.cp.interfaces.IBlock))
