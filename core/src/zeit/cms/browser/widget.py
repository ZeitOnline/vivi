# coding: utf8
from zeit.cms.i18n import MessageFactory as _
import docutils.core
import grokcore.component as grok
import json
import markdown
import markdownify
import pypandoc
import urllib.parse
import time
import xml.sax.saxutils
import zc.datetimewidget.datetimewidget
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.content.add
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zope.app.form.browser
import zope.app.form.browser.sequencewidget
import zope.app.form.browser.widget
import zope.app.form.interfaces
import zope.app.pagetemplate
import zope.cachedescriptors.property
import zope.component
import zope.formlib.interfaces
import zope.formlib.itemswidgets
import zope.formlib.textwidgets
import zope.i18n
import zope.interface
import zope.schema
import zope.schema.interfaces
import zope.traversing.browser.interfaces


class ObjectReferenceWidget(zope.app.form.browser.widget.SimpleInputWidget):
    """DEPRECATED, superceeded by DropObjectWidget"""

    _missing = ''
    template = zope.app.pagetemplate.ViewPageTemplateFile('object-reference-widget.pt')

    def __init__(self, context, source, request):
        super().__init__(context, request)
        self.source = source

    def __call__(self):
        return self.template()

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        content = zeit.cms.interfaces.ICMSContent(input, None)
        if content is None:
            raise zope.app.form.interfaces.ConversionError(_('The object could not be found.'))
        try:
            self.context.validate(content)
        except zope.schema.ValidationError as e:
            self._error = zope.app.form.interfaces.WidgetInputError(
                self.context.__name__, self.label, e
            )
            raise self._error

        return content

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        return value.uniqueId

    @property
    def default_browsing_location(self):
        location = zope.component.queryMultiAdapter(
            (self.context.context, self.source),
            zeit.cms.browser.interfaces.IDefaultBrowsingLocation,
        )
        if location is None:
            return self.repository
        return location

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

    @property
    def type_filter_token(self):
        return self.source.name

    @property
    def show_popup(self):
        """True if the popup should be displayed automatically upon page load."""
        present_marker = self.request.form.get('%s.present' % self.name)
        has_input = self._getFormValue()

        # Only show the object browser when there was no previous input, i.e.
        # when the field was just added. Also only show the object browser
        # automatically when we are in a sequence widget (endswith .)
        if not has_input and not present_marker and self.name.endswith('.'):
            return 'true'

        return 'false'

    @property
    def add_view(self):
        view = self.context.queryTaggedValue('zeit.cms.addform.contextfree')
        if view is None:
            return 'null'
        return "'%s'" % view

    @property
    def workflow(self):
        workflow = zope.component.getMultiAdapter(
            (self._getCurrentValue(), self.request, self),
            zope.viewlet.interfaces.IViewletManager,
            name='zeit.cms.workflow-indicator',
        )
        workflow.update()
        return workflow.render()


class ObjectReferenceSequenceWidget(zope.app.form.browser.sequencewidget.SequenceWidget):
    """DEPRECATED, superceeded by ObjectSequenceWidget"""

    def __call__(self):
        quoted_name = xml.sax.saxutils.quoteattr(self.name)
        result = ['<div id=%s>%s</div>' % (quoted_name, super().__call__())]
        result.append('<script language="javascript">')
        result.append('new zeit.cms.ObjectReferenceSequenceWidget(%s);' % quoted_name)
        result.append('</script>')
        return ''.join(result)


class ObjectReferenceDisplayWidget(zope.app.form.browser.widget.DisplayWidget):
    """DEPRECATED, superceeded by DropObjectDisplayWidget"""

    def __init__(self, context, source, request):
        super().__init__(context, request)
        self.source = source

    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return ''

        url = zope.component.getMultiAdapter(
            (value, self.request), zope.traversing.browser.interfaces.IAbsoluteURL
        )
        link_id = 'link.%s' % time.time()

        link = zope.app.form.browser.widget.renderElement(
            'a', href=url, id=link_id, contents=value.uniqueId
        )
        script = (
            '<script language="javascript">\n' '    new zeit.cms.LinkToolTip("%s")\n' '</script>'
        ) % link_id
        workflow = zope.component.getMultiAdapter(
            (value, self.request, self),
            zope.viewlet.interfaces.IViewletManager,
            name='zeit.cms.workflow-indicator',
        )
        workflow.update()
        return link + '\n' + workflow.render() + '\n' + script


@zope.component.adapter(
    zope.schema.interfaces.ITuple,
    zope.schema.interfaces.IObject,
    zope.publisher.interfaces.browser.IBrowserRequest,
)
@zope.interface.implementer(zope.app.form.interfaces.IInputWidget)
def objectWidgetMultiplexer(context, field, request):
    return zope.component.getMultiAdapter(
        (context, field, field.schema, request), zope.app.form.interfaces.IInputWidget
    )


@zope.component.adapter(
    zope.schema.interfaces.ITuple,
    zope.schema.interfaces.IObject,
    zope.publisher.interfaces.browser.IBrowserRequest,
)
@zope.interface.implementer(zope.app.form.interfaces.IDisplayWidget)
def objectDisplayWidgetMultiplexer(context, field, request):
    return zope.component.getMultiAdapter(
        (context, field, field.schema, request), zope.app.form.interfaces.IDisplayWidget
    )


class AddViewMixin:
    @zope.cachedescriptors.property.Lazy
    def add_view(self):
        if not self.add_type:
            return None
        try:
            context = zeit.cms.content.interfaces.ICommonMetadata(self.context.context)
        except TypeError:
            return None
        adder = zeit.cms.content.add.ContentAdder(
            self.request, self.add_type, context.ressort, context.sub_ressort
        )
        return adder()


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(zeit.cms.content.interfaces.ICommonMetadata)
def find_commonmetadata(context):
    """AddViewMixin needs the ressort of the current content object.
    However, the field the widget is used for might not belong to the content
    object, but to an adapter like an asset reference. Thus, we need to find
    our way back to the actual content object.
    """
    nested_context = getattr(context, 'context', None)
    if zeit.cms.content.interfaces.ICommonMetadata.providedBy(nested_context):
        return nested_context
    return None


class ObjectSequenceWidget(zope.app.form.browser.widget.SimpleInputWidget, AddViewMixin):
    template = zope.app.pagetemplate.ViewPageTemplateFile('objectsequence-edit-widget.pt')

    detail_view_name = '@@object-details'
    cache_object_details = 'true'
    add_type = None
    display_search_button = True
    display_url_field = True

    def __init__(self, context, source, request):
        super().__init__(context, request)
        self.source = source

    def __call__(self):
        return self.template()

    def hasInput(self):
        return self.name + '.count' in self.request.form

    def _toFormValue(self, value):
        result = []
        if value is None:
            return result
        for obj in value:
            if zeit.cms.interfaces.ICMSContent.providedBy(obj):
                result.append({'uniqueId': obj.uniqueId})
        return result

    def _getFormValue(self):
        """Returns a value suitable for use in an HTML form.

        Detects the status of the widget and selects either the input value
        that came from the request, the value from the _data attribute or the
        default value.
        """
        try:
            input_value = self._getCurrentValueHelper()
        except zope.app.form.interfaces.InputErrors:
            items = []
            for entry in self._getFormInput(self._missing):
                items.append({'uniqueId': entry})
            form_value = items
        else:
            form_value = self._toFormValue(input_value)
        return form_value

    def _getFormInput(self, default=None):
        count_str = self.request.get(self.name + '.count')
        if count_str is None:
            return default
        count = int(count_str)
        result = []
        for idx in range(count):
            result.append(self.request.get('%s.%s' % (self.name, idx)))
        return result

    def _toFieldValue(self, value):
        result = []
        for unique_id in value:
            try:
                obj = zeit.cms.interfaces.ICMSContent(unique_id)
            except TypeError:
                raise ContentNotFoundError(unique_id, self.request)
            if obj not in self.source:
                raise WrongContentTypeError(unique_id, self.source.get_check_types(), self.request)
            result.append(obj)
        return tuple(result)

    @property
    def marker(self):
        count = len(self._getFormValue())
        return '<input type="hidden" id="%s.count" name="%s.count" value="%d" />' % (
            self.name,
            self.name,
            count,
        )

    @zope.cachedescriptors.property.Lazy
    def query_view(self):
        return zope.component.queryMultiAdapter(
            (self.source, self.request), zope.formlib.interfaces.ISourceQueryView
        )

    @property
    def accept_classes(self):
        return js_escape_check_types(self.source)

    @property
    def description(self):
        return zope.i18n.translate(self.context.description, context=self.request)


class ObjectSequenceDisplayWidget(zope.app.form.browser.widget.DisplayWidget):
    template = zope.app.pagetemplate.ViewPageTemplateFile('objectsequence-display-widget.pt')

    detail_view_name = '@@object-details'

    def __init__(self, context, source, request):
        super().__init__(context, request)
        self.source = source

    def __call__(self):
        return self.template()

    def get_values(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        result = []
        for obj in value:
            if zeit.cms.interfaces.ICMSContent.providedBy(obj):
                result.append(obj)
        return result


class DropObjectDisplayWidget(ObjectSequenceDisplayWidget):
    def get_values(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value is not None:
            return [value]
        else:
            return []


def js_escape_check_types(source):
    # convert unicode, JS needs 'foo', not 'foo'
    return json.dumps(['type-' + x for x in source.get_check_types()])


class ContentNotFoundError(zope.formlib.interfaces.ConversionError):
    def __init__(self, uniqueId, request):
        msg = _("The object '${id}' could not be found.", mapping={'id': uniqueId})
        msg = zope.i18n.translate(msg, context=request)
        super().__init__(msg)


class WrongContentTypeError(zope.formlib.interfaces.ConversionError):
    def __init__(self, uniqueId, accepted_types, request):
        msg = _(
            "'${id}' does not have an accepted type (${types}).",
            mapping={'id': uniqueId, 'types': ', '.join(accepted_types)},
        )
        msg = zope.i18n.translate(msg, context=request)
        super().__init__(msg)


class DropObjectWidget(zope.app.form.browser.widget.SimpleInputWidget, AddViewMixin):
    template = zope.app.pagetemplate.ViewPageTemplateFile('dropobject-widget.pt')

    detail_view_name = '@@object-details'
    cache_object_details = 'true'
    add_type = None
    display_search_button = True
    display_url_field = True

    def __init__(self, context, source, request):
        super().__init__(context, request)
        self.source = source

    def __call__(self):
        return self.template()

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        try:
            obj = zeit.cms.interfaces.ICMSContent(input)
        except TypeError:
            raise ContentNotFoundError(input, self.request)
        if obj not in self.source:
            raise WrongContentTypeError(input, self.source.get_check_types(), self.request)
        return obj

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        return value.uniqueId

    @property
    def accept_classes(self):
        return js_escape_check_types(self.source)

    @property
    def description(self):
        return zope.i18n.translate(self.context.description, context=self.request)

    @zope.cachedescriptors.property.Lazy
    def query_view(self):
        return zope.component.queryMultiAdapter(
            (self.source, self.request), zope.formlib.interfaces.ISourceQueryView
        )


def ReferenceCollectionInputWidget(field, value_type, request):
    """Widget for Tuple(ReferenceField).

    For simplicity this does not do another lookup according to the source, as
    Tuple(Choice) does in zope.formlib.itemswidget.ChoiceCollectionInputWidget.
    This could be added, of course, but then we'd need another item in the
    discriminator: (field, value_type, source, request) instead of the current
    (field, source, request).
    """
    return ReferenceSequenceWidget(field, value_type.vocabulary, request)


def ReferenceCollectionDisplayWidget(field, value_type, request):
    return ObjectSequenceDisplayWidget(field, value_type.vocabulary, request)


class ReferenceSequenceWidget(ObjectSequenceWidget):
    cache_object_details = 'false'

    def _toFieldValue(self, value):
        result = []
        for unique_id in value:
            result.append(resolve_reference(unique_id, self.context, self.source, self.request))
        return tuple(result)


def resolve_reference(unique_id, field, source, request):
    if not field.context.uniqueId:  # Support AddForms
        params = urllib.parse.parse_qs(urllib.parse.urlparse(unique_id).query)
        if 'target' in params:
            unique_id = params['target'][0]

    try:
        obj = zeit.cms.interfaces.ICMSContent(unique_id)
    except TypeError:
        raise ContentNotFoundError(unique_id, request)

    if not zeit.cms.content.interfaces.IReference.providedBy(obj):
        obj = field.get(field.context).create(obj)

    if obj.target not in source:
        raise WrongContentTypeError(unique_id, source.get_check_types(), request)
    return obj


class ReferenceWidget(DropObjectWidget):
    cache_object_details = 'false'

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        return resolve_reference(input, self.context, self.source, self.request)


DATETIME_WIDGET_ADDITIONAL = """\
<input type="button" value="%(label)s" class="%(css_class)s"
    onclick="javascript:var date = new Date();
        %(increase)s;
        $('%(field)s').value = date.print('%%Y-%%m-%%d %%H:%%M:%%S');
        $('%(field)s').focus();
        MochiKit.Signal.signal(
            '%(field)s', 'onchange', {target: $('%(field)s')});
        " />
"""
DATETIME_WIDGET_INFTY = """\
<input type="button" value="∞" class="infinity"
    onclick="javascript:$('%(field)s').value = '';
        $('%(field)s').focus();
        MochiKit.Signal.signal(
            '%(field)s', 'onchange', {target: $('%(field)s')});
    " />
"""


class DatetimeWidget(zc.datetimewidget.datetimewidget.DatetimeWidget):
    """A datetime widget with additional buttons."""

    def __call__(self):
        html = super().__call__()
        week = DATETIME_WIDGET_ADDITIONAL % {
            'field': self.name,
            'label': '1W',
            'css_class': 'week',
            'increase': 'date.setDate(date.getDate() + 7)',
        }
        month = DATETIME_WIDGET_ADDITIONAL % {
            'field': self.name,
            'label': '1M',
            'css_class': 'month',
            'increase': 'date.setMonth(date.getMonth() + 1)',
        }
        infty = DATETIME_WIDGET_INFTY % {'field': self.name}
        return '<div class="dateTimeWidget">' + html + week + month + infty + '</div>'

    def _configuration(self):
        conf = super()._configuration()
        conf.onClose = "zeit.cms.get_datetime_close('{0}')".format(self.name)
        return conf


class CheckBoxWidget(zope.formlib.boolwidgets.CheckBoxWidget):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.reversed = True

    def __call__(self):
        result = super().__call__()
        result += '\n<span class="checkbox"></span>'
        return result


def CheckboxDisplayWidget(context, request):
    widget = CheckBoxWidget(context, request)
    widget.extra = 'disabled="disabled"'
    return widget


def rst2html(text):
    return docutils.core.publish_parts(
        text, writer_name='html', settings_overrides={'report_level': 5}
    )['fragment']


def html2rst(text):
    try:
        return pypandoc.convert_text(text, to='rst', format='html')
    except OSError:
        return text


class RestructuredTextWidget(zope.formlib.textwidgets.TextAreaWidget):
    template = zope.app.pagetemplate.ViewPageTemplateFile('rst-widget.pt')

    def __call__(self):
        self.textarea = super().__call__()
        return self.template()

    @property
    def rendered_content(self):
        return rst2html(self._getFormValue())


class ConvertingRestructuredTextWidget(RestructuredTextWidget):
    def _toFieldValue(self, value):
        value = super()._toFieldValue(value)
        return rst2html(value)

    def _toFormValue(self, value):
        value = super()._toFormValue(value)
        return html2rst(value)


class RestructuredTextDisplayWidget(zope.formlib.widgets.DisplayWidget):
    def __call__(self):
        value = super().__call__()
        return '<div class="rst-display-widget">%s</div>' % rst2html(value) if value else value


class AutocompleteWidget(zope.formlib.textwidgets.TextWidget):
    cssClass = 'autocomplete-widget'

    def __init__(self, context, source, request):
        super().__init__(context, request)
        self.source = source
        self.extra = 'cms:autocomplete-source="%s"' % (self.query_url)

    @property
    def query_url(self):
        return zope.component.queryMultiAdapter(
            (self.source, self.request), zeit.cms.browser.interfaces.ISourceQueryURL
        )


class AutocompleteDisplayWidget(zope.formlib.widgets.DisplayWidget):
    def __init__(self, context, source, request):
        super().__init__(context, request)


class AutocompleteSourceQuery(grok.MultiAdapter, zeit.cms.browser.view.Base):
    grok.adapts(
        zeit.cms.content.interfaces.IAutocompleteSource, zeit.cms.browser.interfaces.ICMSLayer
    )
    grok.provides(zope.formlib.interfaces.ISourceQueryView)

    def __init__(self, source, request):
        self.source = source
        self.request = request

    def __call__(self):
        return (
            '<input type="text" class="autocomplete" '
            'placeholder={placeholder} '
            'cms:autocomplete-source="{url}" />'
        ).format(
            url=zope.component.queryMultiAdapter(
                (self.source, self.request), zeit.cms.browser.interfaces.ISourceQueryURL
            ),
            placeholder=xml.sax.saxutils.quoteattr(
                zope.i18n.translate(_('Type to find entries ...'), context=self.request)
            ),
        )


class ColorpickerWidget(zope.formlib.textwidgets.TextWidget):
    cssClass = 'colorpicker-widget'


def empty_toFieldValue(self, input):
    # XXX Work around formlib bug, browser always POSTs the parameter with
    # no value, which somehow gets converted to a list containing an empty
    # string [''], which formlib does not expect.
    if input == ['']:
        input = None
    return orig_toFieldValue(self, input)


orig_toFieldValue = zope.formlib.itemswidgets.MultiDataHelper._toFieldValue
zope.formlib.itemswidgets.MultiDataHelper._toFieldValue = empty_toFieldValue


class MarkdownWidget(zope.formlib.textwidgets.TextAreaWidget):
    def _toFieldValue(self, value):
        value = super()._toFieldValue(value)
        if not value:
            return value
        try:
            return markdown.markdown(value)
        except OSError:
            return value

    def _toFormValue(self, value):
        value = super()._toFormValue(value)
        try:
            return markdownify.markdownify(value, heading_style='ATX')
        except OSError:
            return value


class MarkdownDisplayWidget(zope.formlib.widget.DisplayWidget):
    def __call__(self):
        """Copy&Paste from superclass to *not* XML escape the value."""
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            value = ''
        return '<div class="markdown-display-widget">%s</div>' % value


def TupleSequenceWidget(field, source, request):
    ignored = None
    return zope.formlib.sequencewidget.TupleSequenceWidget(field, ignored, request)


class DurationDisplayWidget(zope.formlib.widget.DisplayWidget):
    """Display widget for :py:class:`zeit.cms.content.field.DurationField`."""

    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return ''

        return readable_duration(value)


def readable_duration(value):
    """Converts seconds to human readable format 'hh:mm:ss'.

    e.g.:
    - int 160 -> str '2:40'
    - int 7200 -> str '2:00:00'
    """
    if not value or value < 0:
        return ''
    hours, remainder = divmod(value, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    else:
        return f'{minutes:02d}:{seconds:02d}'
