from zeit.content.cp.interfaces import IAutomaticArea
import gocept.form.grouped
import zeit.cms.interfaces
import zeit.content.cp.browser.blocks.teaser
import zeit.content.cp.interfaces
import zeit.edit.browser.block
import zeit.edit.browser.view
import zope.formlib.form


class ViewletManager(zeit.edit.browser.block.BlockViewletManager):

    @property
    def css_class(self):
        classes = super(ViewletManager, self).css_class
        visible = 'block-visible-off' if not self.context.visible else ''
        return ' '.join(['editable-area', visible, classes])


class AreaViewletManager(ViewletManager):

    @property
    def css_class(self):
        classes = super(AreaViewletManager, self).css_class

        area = IAutomaticArea(self.context)
        if not zeit.content.cp.interfaces.\
                automatic_area_can_read_teasers_automatically(area):
            automatic = 'block-automatic-not-possible'
        else:
            if area.automatic:
                automatic = 'block-automatic-on'
            else:
                automatic = 'block-automatic-off'

        return ' '.join(['editable-area', automatic, classes])


class EditProperties(zeit.content.cp.browser.blocks.teaser.EditLayout):

    interface = zeit.content.cp.interfaces.IArea
    layout_prefix = 'teaserbar'  # XXX should be area


class EditCommon(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IArea).select(
            'width', 'supertitle', 'title', 'teaserText')


class EditOverflow(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IArea).select(
            'block_max', 'overflow_into')


class EditAutomatic(zeit.content.cp.browser.blocks.teaser.EditCommon):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.IAutomaticArea).select(
            'count', 'query', 'raw_query', 'automatic',
            'automatic_type', 'referenced_cp', 'hide_dupes')

    # XXX Kludgy: ``automatic`` must come after ``count``, since setting
    # automatic to True needs to know the teaser count. Thus we order the
    # form_fields accordingly, and alter the display order using field_groups.
    field_groups = (gocept.form.grouped.Fields(
        '', ('automatic', 'count', 'automatic_type', 'referenced_cp',
             'hide_dupes', 'query', 'raw_query')),)

    template = zope.browserpage.ViewPageTemplateFile(
        'blocks/teaser.edit-common.pt')


class ChangeLayout(zeit.content.cp.browser.blocks.teaser.ChangeLayout):

    interface = zeit.content.cp.interfaces.IArea


class SchematicPreview(object):

    prefix = 'http://xml.zeit.de/data/cp-area-schemas/{}.svg'

    def areas(self):
        region = zeit.content.cp.interfaces.IRegion(self.context)
        return region.values()

    def preview(self, area):
        content = zeit.cms.interfaces.ICMSContent(self.prefix.format(
            area.width.replace('/', '_')))
        return content.open().read()

    def css_class(self, area):
        classes = ['area-preview-image']
        if area == self.context:
            classes.append('active')
        return ' '.join(classes)
