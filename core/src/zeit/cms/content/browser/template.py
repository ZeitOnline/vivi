# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import z3c.menu.simple.menu
import zc.table.column
import zc.table.table
import zeit.cms.browser.column
import zeit.cms.browser.form
import zeit.cms.browser.listing
import zeit.cms.content.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.template
import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.publisher.interfaces.browser


class Manager(object):

    title = _("Templates")

    @zope.cachedescriptors.property.Lazy
    def template_managers(self):
        result = []
        for name, utility in sorted(zope.component.getUtilitiesFor(
            zeit.cms.content.interfaces.ITemplateManager)):
            result.append(dict(
                name=name,
                manager=utility))
        return result


class Listing(zeit.cms.browser.listing.Listing):

    title = _("Templates")
    filter_interface = zope.interface.Interface
    css_class = 'contentListing'

    columns = (
        zc.table.column.SelectionColumn(
            idgetter=lambda item: item.__name__),
        zeit.cms.browser.column.LinkColumn(
            title=_('Title'),
            cell_formatter=lambda v, i, f: i.title),
    )

    @property
    def content(self):
        return self.context.values()


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ITemplate).select('title', 'xml')


class Add(FormBase, zeit.cms.browser.form.AddForm):

    title = _("Add template")
    factory = zeit.cms.content.template.Template
    next_view = 'webdav-properties.html'

    def suggestName(self, object):
        return object.title


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _("Edit template")


class Properties(object):

    title = _("Edit webdav properties")

    def update(self):
        if 'dav.save' in self.request:
            data = zip(self.request['name'], self.request['namespace'],
                       self.request['value'])
            new_properties = dict(
                ((item[0], item[1]), item[2])
                for item in data
                if item[0] and item[1])
            properties = zeit.connector.interfaces.IWebDAVWriteProperties(
                self.context)
            properties.update(new_properties)

    @property
    def content(self):
        properties = zeit.connector.interfaces.IWebDAVReadProperties(
            self.context)
        return [
            dict(namespace=item[0][1],
                 name=item[0][0],
                 value=item[1])
            for item in properties.items()]


class ChooseTemplateForm(gocept.form.grouped.Form):
    """Base class for template choose forms.
    """

    title = _("Choose template")
    add_view = None

    @zope.formlib.form.action(_("Continue"))
    def handle_choose_template(self, action, data):
        session = zope.session.interfaces.ISession(self.request)
        session[self.add_view]['template'] = data['template']
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name='absolute_url')
        self.request.response.redirect(
            '%s/@@%s' % (url, self.add_view))


def TemplateChooserSchema(source_name):

    class ITemplateChooserSchema(zope.interface.Interface):
        """Schema to choose template."""

        template = zope.schema.Choice(
            title=_("Template"),
            required=False,
            source=zeit.cms.content.template.BasicTemplateSource(source_name))

    return ITemplateChooserSchema


class TemplateWidgetSetup(object):

    zope.component.adapts(zope.publisher.interfaces.browser.IBrowserPage)
    zope.interface.implements(
        zeit.cms.content.browser.interfaces.ITemplateWidgetSetup)

    def __init__(self, context):
        self.context = context
        self.request = context.request

    def setup_widgets(self, widgets, session_key, chooser_schema,
                      ignore_request=False):
        session = zope.session.interfaces.ISession(self.request)
        template = session[session_key].get('template')
        if not ignore_request and template:
            adapters = {}
            for widget in widgets:
                field = widget.context
                name = widget.context.__name__
                form_field = self.context.form_fields[name]

                # Adapt context, if necessary
                interface = form_field.interface
                if interface == chooser_schema:
                    value = template
                else:
                    adapter = adapters.get(interface)
                    if adapter is None:
                        if interface is None:
                            adapter = template
                        else:
                            adapter = interface(template)
                        adapters[interface] = adapter
                    value = field.get(adapter)
                if value and value != field.default:
                    widget.setRenderedValue(value)


class MenuItem(zeit.cms.browser.menu.GlobalMenuItem):

    title = _("Templates")
    viewURL = 'templates'
    pathitem = 'templates'
