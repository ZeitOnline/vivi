# -*- coding: utf-8 -*-
import zope.formlib.form

import zeit.cms.browser.widget
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):
    form_fields = zope.formlib.form.Fields(zeit.content.cp.interfaces.INewsletterSignupBlock).omit(
        *list(zeit.content.cp.interfaces.IBlock)
    )
    form_fields['prefix_text'].custom_widget = zeit.cms.browser.widget.MarkdownWidget

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['prefix_text'].height = 50
