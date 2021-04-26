from zeit.cms.i18n import MessageFactory as _
import commentjson
import pygments
import pygments.formatters
import pygments.lexers
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.repository.browser.adapter
import zeit.content.text.interfaces
import zeit.content.text.json
import zope.component
import zope.formlib.form
import zope.formlib.textwidgets
import zope.formlib.widget
import zope.interface
import zope.publisher.interfaces


class FormBase:

    form_fields = zope.formlib.form.FormFields(
        zeit.content.text.interfaces.IJSON).omit('encoding')


class Add(FormBase, zeit.cms.browser.form.AddForm):

    title = _('Add JSON file')
    factory = zeit.content.text.json.JSON


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit JSON file')


class Display(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('View JSON file')


class JSONInputWidget(zope.formlib.textwidgets.TextAreaWidget):

    def _toFieldValue(self, input):
        value = super()._toFieldValue(input)
        try:
            commentjson.loads(value)
        except Exception as e:
            raise zope.app.form.interfaces.ConversionError(e)
        return value


class JSONDisplayWidget(zope.formlib.widget.DisplayWidget):

    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default
        if not content:
            return ''
        return pygments.highlight(
            content, pygments.lexers.JsonLexer(),
            pygments.formatters.HtmlFormatter(cssclass='pygments'))
