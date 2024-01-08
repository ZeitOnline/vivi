import zope.formlib.form
import zope.formlib.interfaces
import zope.formlib.namedtemplate

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.interfaces


form_template = zope.formlib.namedtemplate.NamedTemplateImplementation(
    zope.app.pagetemplate.ViewPageTemplateFile('sourceedit.pt'), zope.formlib.interfaces.IPageForm
)


class TextEditForm(zope.formlib.form.EditForm):
    """Edit form allowing source editing."""

    template = zope.formlib.namedtemplate.NamedTemplate('sourceedit_form')

    form_fields = zope.formlib.form.Fields(zeit.cms.content.interfaces.ITextContent).select('data')


class XMLBaseForm:
    template = zope.formlib.namedtemplate.NamedTemplate('sourceedit_form')
    form_fields = zope.formlib.form.Fields(zeit.cms.content.interfaces.IXMLContent).select('xml')


class XMLEditForm(XMLBaseForm, zope.formlib.form.EditForm):
    """Edit form allowing source editing."""

    title = _('Edit source code')


class XMLDisplayForm(XMLBaseForm, zope.formlib.form.DisplayForm):
    title = _('View source code')


@zope.component.adapter(zeit.cms.content.interfaces.IXMLContent)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def edit_view_name(context):
    return 'xml_source_edit.html'


@zope.component.adapter(zeit.cms.content.interfaces.IXMLContent)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDisplayViewName)
def display_view_name(context):
    return 'xml_source_view.html'
