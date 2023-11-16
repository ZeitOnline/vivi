import json
import lxml.etree
import pygments
import pygments.formatters
import pygments.lexers
import zc.form.browser.combinationwidget
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zope.app.form.browser.interfaces
import zope.app.form.browser.textwidgets
import zope.app.form.browser.widget
import zope.app.form.interfaces
import zope.app.pagetemplate
import zope.component
import zope.formlib.widgets
import zope.interface


class XMLTreeWidget(zope.app.form.browser.textwidgets.TextAreaWidget):
    def _toFieldValue(self, input):
        try:
            return self.context.fromUnicode(input)
        except zope.schema.ValidationError as e:
            raise zope.app.form.interfaces.ConversionError(e)

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        else:
            # Etree very explicitly checks for the type and doesn't like a
            # proxied object
            value = zope.proxy.removeAllProxies(value)
            if value.getparent() is None:
                # When we're editing the whole tree we want to serialize the
                # root tree to get processing instructions.
                value = value.getroottree()
            return lxml.etree.tounicode(value, pretty_print=True).replace('\n', '\r\n')


class XMLTreeDisplayWidget(zope.app.form.browser.widget.DisplayWidget):
    def __call__(self):
        if self._renderedValueSet():
            content = self._data
            content = zope.proxy.removeAllProxies(content)
            content = lxml.etree.tostring(content, pretty_print=True, encoding=str)
        else:
            content = self.context.default
        if not content:
            return ''
        return pygments.highlight(
            content,
            pygments.lexers.XmlLexer(),
            pygments.formatters.HtmlFormatter(cssclass='pygments'),
        )


class CombinationWidget(zc.form.browser.combinationwidget.CombinationWidget):
    """Subclassed combination widget to change the template.

    NamedTemplate doesn't take the request into account so we cannot register a
    new template in our skin. This sucks.

    """

    template = zope.app.pagetemplate.ViewPageTemplateFile('combinationwidget.pt')


class ParentChildDropdownUpdater:
    parent_source = NotImplemented
    child_source = NotImplemented

    def __init__(self, context, request):
        super().__init__(context, request)
        self.parent_source = self.parent_source(self.context)
        self.parent_terms = zope.component.getMultiAdapter(
            (self.parent_source, request), zope.app.form.browser.interfaces.ITerms
        )

    def get_result(self, parent_token):
        try:
            parent_value = self.parent_terms.getValue(parent_token)
        except KeyError:
            return []

        @zope.interface.implementer(self.child_source.factory.parent_value_iface)
        class Fake:
            pass

        fake = Fake()
        setattr(fake, self.child_source.factory.parent_value_key, parent_value)

        source = self.child_source(fake)
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.app.form.browser.interfaces.ITerms
        )
        result = []
        for value in source:
            term = terms.getTerm(value)
            result.append((term.title, term.token))

        return sorted(result)

    def __call__(self, parent_token):
        result = self.get_result(parent_token)
        self.request.response.setHeader('Cache-Control', 'public;max-age=3600')
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(sorted(result)).encode('utf8')


class SubNavigationUpdater(ParentChildDropdownUpdater):
    parent_source = zeit.cms.content.sources.RessortSource()
    child_source = zeit.cms.content.sources.SubRessortSource()


class ChannelUpdater(ParentChildDropdownUpdater):
    parent_source = zeit.cms.content.sources.ChannelSource()
    child_source = zeit.cms.content.sources.SubChannelSource()
