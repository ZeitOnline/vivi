from zeit.cms.i18n import MessageFactory as _
from zope.cachedescriptors.property import Lazy as cachedproperty
import gocept.form.grouped
import zeit.cms.content.browser.widget
import zeit.cms.interfaces
import zeit.content.cp.browser.blocks.teaser
import zeit.content.cp.browser.view
import zeit.content.cp.interfaces
import zeit.edit.browser.block
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.formlib.widgets


class ViewletManager(zeit.edit.browser.block.BlockViewletManager):

    @property
    def css_class(self):
        classes = super().css_class
        visible = 'block-visible-off' if not self.context.visible else ''
        return ' '.join(['editable-area', visible, classes])


class AreaViewletManager(ViewletManager):

    @property
    def css_class(self):
        classes = super().css_class

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
        'topiclink_label_1', 'topiclink_url_1', 'topiclink_label_2',
        'topiclink_url_2', 'topiclink_label_3', 'topiclink_url_3',
        'background_color')


class EditOverflow(zeit.content.cp.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IArea).select(
            'block_max', 'overflow_into')


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
            (field, self.request), self.widget_interface)
        widget.setPrefix(self.name + ".")
        return widget

    def setRenderedValue(self, value):
        super().setRenderedValue(value)
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
                len(value)
            except (TypeError, AttributeError):
                value = missing_value
            # patched
            # | else:
            # |    if len_value != len(field.fields):
            # |        value = missing_value
        if value is not missing_value:
            hasInput = self.hasInput()
            for w, v in map(lambda *args: args, self.widgets, value):
                if not hasInput or v != w.context.missing_value:
                    w.setRenderedValue(v)
        for w in self.widgets:
            if zope.schema.interfaces.IBool.providedBy(w.context):
                w.invert_label = True
            else:
                w.invert_label = False
        return self.template()

    def loadValueFromRequest(self):
        """copy&paste from superclass to catch ConversionError and
        ValidationError (which most likely occur due to the subfield type being
        changed), and replace the actual value with missing_value in that case.
        """
        field = self.context
        missing_value = field.missing_value
        widgets = self.widgets
        required_errors = []
        errors = []
        values = []
        any = False
        for w in widgets:
            try:
                val = w.getInputValue()
            except zope.formlib.interfaces.WidgetInputError as e:
                if isinstance(getattr(e, 'errors'),  # noqa
                              zope.schema.interfaces.RequiredMissing):
                    required_errors.append((w, e))
                else:
                    errors.append((w, e))
                val = w.context.missing_value
            except zope.formlib.interfaces.InputErrors:  # patched
                val = w.context.missing_value
                # sub-widgets render themselves independently, so we have to
                # remove the erroneous value from the request entirely.
                self.request.form.pop(w.name, None)
            values.append(val)
            any = any or val != w.context.missing_value
        if field.required or any or errors:
            errors.extend(required_errors)
        else:  # remove the required errors in the sub widgets
            for w, _e in required_errors:
                w.error = lambda: None
        if errors:
            if len(errors) == 1:
                errors = errors[0][1]
            else:
                errors = [e for widget, e in errors]
            self._error = zope.formlib.interfaces.WidgetInputError(
                self.context.__name__, self.label, errors)
            values = missing_value
        elif not any:
            values = missing_value
        else:
            values = tuple(values)
        return values


class EditAutomatic(zeit.content.cp.browser.blocks.teaser.EditCommon):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.IArea).select(
            'count', 'query', 'query_order',
            'elasticsearch_raw_query', 'elasticsearch_raw_order',
            'is_complete_query',
            'automatic', 'automatic_type',
            'hide_dupes', 'consider_for_dupes',
            'referenced_cp',
            'referenced_topicpage', 'topicpage_filter', 'topicpage_order',
            'topicpagelist_order',
            'related_topicpage',
            'rss_feed',
            'reach_service', 'reach_section', 'reach_access', 'reach_age')

    field_groups = (
        # XXX Kludgy: ``automatic`` must come after ``count``, since setting
        # automatic to True needs to know the teaser count. Thus, we order the
        # form_fields accordingly, and alter the _display_ order here.
        gocept.form.grouped.Fields(
            '', ('automatic_type', 'automatic', 'count',
                 'hide_dupes', 'consider_for_dupes')),
        gocept.form.grouped.Fields(
            _('automatic-area-type-centerpage'), ('referenced_cp',)),
        gocept.form.grouped.Fields(
            _('automatic-area-type-rss-feed'), ('rss_feed',)),
        gocept.form.grouped.Fields(
            _('automatic-area-type-custom'), ('query', 'query_order')),
        gocept.form.grouped.Fields(
            _('automatic-area-type-topicpage'), (
                'referenced_topicpage', 'topicpage_filter',
                'topicpage_order')),
        gocept.form.grouped.Fields(
            _('automatic-area-type-elasticsearch-query'),
             ('elasticsearch_raw_query', 'is_complete_query',
              'elasticsearch_raw_order')),
        gocept.form.grouped.Fields(
            _('automatic-area-type-related-topics'), ('related_topicpage', )),
        gocept.form.grouped.Fields(
            _('automatic-area-type-reach'),
             ('reach_service', 'reach_section', 'reach_access', 'reach_age')),
    )

    template = zope.browserpage.ViewPageTemplateFile(
        'blocks/teaser.edit-common.pt')

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['automatic'].reversed = False


class ChangeLayout(zeit.content.cp.browser.blocks.teaser.ChangeLayout):

    interface = zeit.content.cp.interfaces.IArea


class SchematicPreview:

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


class Fold(zeit.cms.browser.view.Base):

    def title(self):
        return ''  # Already covered by layout.element.title.pt
