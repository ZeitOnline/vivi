# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.blocks.teaser
import zeit.content.cp.interfaces
import zeit.edit.browser.block
import zeit.edit.browser.view
import zope.formlib.form


class ViewletManager(zeit.edit.browser.block.BlockViewletManager):

    @property
    def css_class(self):
        classes = super(ViewletManager, self).css_class
        return ' '.join(['editable-area', classes])


class EditProperties(zeit.content.cp.browser.blocks.teaser.EditLayout):

    interface = zeit.content.cp.interfaces.IArea
    layout_prefix = 'teaserbar'  # XXX should be area


class EditCommon(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IArea).select(
        'width', 'supertitle', 'title', 'teaserText', 'background_color',
        '__name__')
    form_fields['background_color'].custom_widget = (
        zeit.cms.browser.widget.ColorpickerWidget)


class ChangeLayout(zeit.content.cp.browser.blocks.teaser.ChangeLayout):

    interface = zeit.content.cp.interfaces.IArea
