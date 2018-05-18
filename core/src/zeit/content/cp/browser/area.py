from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import pysolr
import zeit.cms.interfaces
import zeit.content.cp.browser.blocks.teaser
import zeit.content.cp.browser.view
import zeit.content.cp.interfaces
import zeit.edit.browser.block
import zeit.solr.interfaces
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.formlib.widgets


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

        if not zeit.content.cp.interfaces.\
                automatic_area_can_read_teasers_automatically(self.context):
            automatic = 'block-automatic-not-possible'
        else:
            if self.context.automatic:
                automatic = 'block-automatic-on'
            else:
                automatic = 'block-automatic-off'

        return ' '.join(['editable-area', automatic, classes])


class EditCommon(zeit.content.cp.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IArea).select(
            'supertitle', 'title', 'read_more', 'read_more_url', 'image',
            'visible_mobile')


class EditOverflow(zeit.content.cp.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IArea).select(
            'block_max', 'overflow_into')


class SolrQueryWidget(zope.formlib.widgets.TextAreaWidget):

    def _toFieldValue(self, value):
        value = super(SolrQueryWidget, self)._toFieldValue(value)
        solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        try:
            solr.search(value, rows=1)
        except pysolr.SolrError:
            raise zope.formlib.interfaces.ConversionError(
                _('Invalid solr query'), value)
        return value


class EditAutomatic(zeit.content.cp.browser.blocks.teaser.EditCommon):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.IArea).select(
            'count', 'query', 'query_order', 'raw_query', 'raw_order',
            'elasticsearch_raw_query', 'elasticsearch_raw_order',
            'is_complete_query',
            'automatic', 'automatic_type', 'referenced_cp', 'hide_dupes',
            'referenced_topicpage', 'topicpage_filter')
    form_fields['raw_query'].custom_widget = SolrQueryWidget

    field_groups = (
        # XXX Kludgy: ``automatic`` must come after ``count``, since setting
        # automatic to True needs to know the teaser count. Thus, we order the
        # form_fields accordingly, and alter the _display_ order here.
        gocept.form.grouped.Fields(
            '', ('automatic_type', 'automatic', 'count', 'hide_dupes')),
        gocept.form.grouped.Fields(
            _('automatic-area-type-centerpage'), ('referenced_cp',)),
        gocept.form.grouped.Fields(
            _('automatic-area-type-channel'), ('query', 'query_order')),
        gocept.form.grouped.Fields(
            _('automatic-area-type-topicpage'), (
                'referenced_topicpage', 'topicpage_filter')),
        gocept.form.grouped.Fields(
            _('automatic-area-type-query'), ('raw_query', 'raw_order')),
        gocept.form.grouped.Fields(
            _('automatic-area-type-elasticsearch-query'),
             ('elasticsearch_raw_query', 'is_complete_query',
              'elasticsearch_raw_order')),
    )

    template = zope.browserpage.ViewPageTemplateFile(
        'blocks/teaser.edit-common.pt')

    def setUpWidgets(self, *args, **kw):
        super(EditAutomatic, self).setUpWidgets(*args, **kw)
        self.widgets['automatic'].reversed = False


class ChangeLayout(zeit.content.cp.browser.blocks.teaser.ChangeLayout):

    interface = zeit.content.cp.interfaces.IArea


class SchematicPreview(object):

    prefix = 'http://xml.zeit.de/data/cp-area-schemas/{}.svg'

    def areas(self):
        region = zeit.content.cp.interfaces.IRegion(self.context)
        return region.values()

    def preview(self, area):
        content = zeit.cms.interfaces.ICMSContent(
            self.prefix.format(area.kind))
        return content.open().read()

    def css_class(self, area):
        classes = ['area-preview-image']
        if area == self.context:
            classes.append('active')
        return ' '.join(classes)
