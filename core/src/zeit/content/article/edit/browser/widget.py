import zeit.cms.content.browser.widget
from zope.cachedescriptors.property import Lazy as cachedproperty
import zope.formlib.interfaces
import zope.component
import logging

log = logging.getLogger(__name__)


class DynamicCombinationWidget2(
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
                log.error('Widget Input Error')
                pass
        elif self._renderedValueSet():
            log.error('no Input')
            # selector = self._data[0]

        for field in self.context.generate_fields(selector):
            result.append(self._create_widget(field))
        return result

    def _create_widget(self, field):
        widget = zope.component.getMultiAdapter(
            (field, self.request), self.widget_interface)
        widget.setPrefix(self.name + ".")
        return widget

    def setRenderedValue(self, value):
        super(DynamicCombinationWidget2, self).setRenderedValue(value)
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
        log.info('render {}'.format(self.widgets))
        field = self.context
        missing_value = field.missing_value
        if value is not missing_value:
            try:
                len(value)
            except (TypeError, AttributeError):
                value = missing_value
            # patched
            # else:
            #     if len_value != len(field.fields):
            #         value = missing_value
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
        log.info('loadValueFromRequest')
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
                if isinstance(getattr(e, 'errors'),
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
            for w, e in required_errors:
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
