from zeit.cms.i18n import MessageFactory as _
from zope.cachedescriptors.property import Lazy as cachedproperty
import gocept.form.grouped
import pysolr
import zeit.cms.content.browser.widget
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


class DynamicCombinationWidget(
        zeit.cms.content.browser.widget.CombinationWidget):
    """Determines which further subwidgets to render according to the value of
    the first subwidget.
    """

    @cachedproperty
    def widgets(self):
        type_field = self.context.type_field.bind(self.context.context)
        selector = type_field.default
        result = [self._create_widget(type_field)]
        if self.hasInput():
            try:
                selector = result[0].getInputValue()
            except zope.formlib.interfaces.WidgetInputError:
                pass
        elif self._renderedValueSet():
            selector = self._data[0]
        for field in self.context.generate_fields(selector):
            result.append(self._create_widget(field))
        return result

    def _create_widget(self, field):
        widget = zope.component.getMultiAdapter(
            (field, self.request,), self.widget_interface)
        widget.setPrefix(self.name + ".")
        return widget

    def setRenderedValue(self, value):
        super(DynamicCombinationWidget, self).setRenderedValue(value)
        # SequenceWidget calls setPrefix first and setRenderedValue later, so
        # when self.widgets is called the first time, self._data has not been
        # set yet. Thus we have to recreate the widgets, now that we know the
        # correct type. Also, SequenceWidget calls setRenderedValue(None) as
        # a default (which is kind of invalid), so we have to ignore that.
        if value is not None:
            self.__dict__.pop('widgets', None)

    def render(self, value):
        """copy&paste from superclass to remove check that value matches
        the configured subfields -- as our subfields are dynamic.
        """
        field = self.context
        missing_value = field.missing_value
        if value is not missing_value:
            try:
                len_value = len(value)
            except (TypeError, AttributeError):
                value = missing_value
            # else:
            #     if len_value != len(field.fields):
            #         value = missing_value
        if value is not missing_value:
            hasInput = self.hasInput()
            for w, v in map(None, self.widgets, value):
                if not hasInput or v != w.context.missing_value:
                    w.setRenderedValue(v)
        for w in self.widgets:
            if zope.schema.interfaces.IBool.providedBy(w.context):
                w.invert_label = True
            else:
                w.invert_label = False
        return self.template()


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
