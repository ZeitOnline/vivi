import gocept.form.grouped
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


class EditAutomatic(zeit.content.cp.browser.blocks.teaser.EditCommon):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.IAutomaticArea).select(
            'count', 'query', 'raw_query', 'automatic')

    # XXX Kludgy: ``automatic`` must come after ``count``, since setting
    # automatic to True needs to know the teaser count. Thus we order the
    # form_fields accordingly, and alter the display order using field_groups.
    field_groups = (gocept.form.grouped.Fields(
        '', ('automatic', 'count', 'query', 'raw_query')),)

    template = zope.browserpage.ViewPageTemplateFile(
        'blocks/teaser.edit-common.pt')


class ChangeLayout(zeit.content.cp.browser.blocks.teaser.ChangeLayout):

    interface = zeit.content.cp.interfaces.IArea
