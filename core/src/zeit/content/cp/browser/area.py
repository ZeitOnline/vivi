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
            'width', 'supertitle', 'title', 'teaserText')


class EditAutomatic(
        zope.formlib.form.SubPageEditForm,
        zeit.cms.browser.form.WidgetCSSMixin):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.IAutomaticArea,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'automatic', 'count', 'query', 'raw_query')


class ChangeLayout(zeit.content.cp.browser.blocks.teaser.ChangeLayout):

    interface = zeit.content.cp.interfaces.IArea
