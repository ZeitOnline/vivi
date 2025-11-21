import json

import lxml.etree
import pygments
import pygments.formatters
import pygments.lexers
import zc.form.browser.combinationwidget
import zope.app.pagetemplate
import zope.browser.interfaces
import zope.component
import zope.formlib.interfaces
import zope.formlib.source
import zope.formlib.textwidgets
import zope.formlib.widget
import zope.formlib.widgets
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.content.sources


class XMLTreeWidget(zope.formlib.textwidgets.TextAreaWidget):
    def _toFieldValue(self, input):
        try:
            return self.context.fromUnicode(input)
        except zope.schema.ValidationError as e:
            raise zope.formlib.interfaces.ConversionError(e)

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


class XMLTreeDisplayWidget(zope.formlib.widget.DisplayWidget):
    def __call__(self):
        if self._renderedValueSet():
            content = self._data
            content = zope.proxy.removeAllProxies(content)
            lxml.etree.indent(content)
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
            (self.parent_source, request), zope.browser.interfaces.ITerms
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
            (source, self.request), zope.browser.interfaces.ITerms
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


class PermissiveDropdownWidget(zope.formlib.source.SourceDropdownWidget):
    def renderItemsWithValues(self, values):
        result = super().renderItemsWithValues(values)
        # copy&paste from superclass. Seems rather inconsistent that `values`
        # contains "form value" when missing, but "field value" otherwise.
        missing = self._toFormValue(self.context.missing_value)
        if missing not in values and len(values) == 1 and values[0] not in self.vocabulary:
            result.insert(
                0,
                self.renderSelectedItem(
                    None,
                    zope.i18n.translate(
                        _('Obsolete value ${value}', mapping={'value': values[0]}),
                        context=self.request,
                    ),
                    self.vocabulary.getTerm(values[0]).token,
                    self.name,
                    self.cssClass + ' unknown',
                ),
            )
        return result
