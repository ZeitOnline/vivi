# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.blocks.teaser
import zeit.content.cp.interfaces
import zope.component


class AreaViewletManager(zeit.edit.browser.block.BlockViewletManager):

    @property
    def css_class(self):
        classes = super(AreaViewletManager, self).css_class
        return ' '.join(['editable-area', classes])


class EditProperties(zeit.content.cp.browser.blocks.teaser.EditProperties):

    interface = zeit.content.cp.interfaces.IArea
    layout_prefix = 'teaserbar'  # XXX should be removed
    layouts = ()

    form_fields = []

    @property
    def form(self):
        return ''


class EditCommon(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IArea).select(
        'supertitle', 'teaserText', 'background_color')
    form_fields['background_color'].custom_widget = (
        zeit.cms.browser.widget.ColorpickerWidget)
