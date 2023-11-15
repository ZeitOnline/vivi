import lxml.etree
import pygments
import pygments.formatters
import pygments.lexers
import zeit.cms.browser.view
import zope.proxy

form_template = zope.formlib.namedtemplate.NamedTemplateImplementation(
    zope.app.pagetemplate.ViewPageTemplateFile('xml.edit-contents.pt'),
    zope.formlib.interfaces.IPageForm,
)


class Display(zeit.cms.browser.view.Base):
    @property
    def css_class(self):
        return 'xml-block'

    def update(self):
        content = zope.proxy.removeAllProxies(self.context.xml)
        content = lxml.etree.tounicode(content, pretty_print=True)
        self.xml = pygments.highlight(
            content,
            pygments.lexers.XmlLexer(),
            pygments.formatters.HtmlFormatter(cssclass='pygments'),
        )


class EditProperties(zeit.cms.browser.sourceedit.XMLEditForm):
    template = zope.formlib.namedtemplate.NamedTemplate('xmledit_form')

    form_fields = zope.formlib.form.Fields(zeit.content.cp.interfaces.IXMLBlock).select('xml')
