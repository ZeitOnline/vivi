# Copyright (c) 2006-2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form
import zope.formlib.namedtemplate
import zope.formlib.interfaces

import zope.app.container.interfaces
import zope.app.pagetemplate

import zeit.cms.checkout.interfaces


zeit_form_template = zope.formlib.namedtemplate.NamedTemplateImplementation(
    zope.app.pagetemplate.ViewPageTemplateFile('form.pt'),
    zope.formlib.interfaces.IPageForm)
REMAINING_FIELDS = object()

class WidgetGroup(object):

    widgets = None

    def __init__(self, title, css_class=None):
        self.title = title
        self.css_class = css_class


class FormBase(object):

    template = zope.formlib.namedtemplate.NamedTemplate('zeitform')
    widget_groups = ()


    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = None
        remainder_group = None
        fields = []
        self.groups = []

        for title, field_names, css_class in self.widget_groups:
            widget_group = WidgetGroup(title, css_class)

            if field_names is REMAINING_FIELDS:
                widgets = None
                remainder_group = widget_group
            else:
                widgets = self._get_widgets(self.form_fields.select(
                    *field_names), ignore_request)
                if self.widgets is None:
                    self.widgets = widgets
                else:
                    self.widgets += widgets
                fields.extend(field_names)

            widget_group.widgets = widgets
            self.groups.append(widget_group)

        # we create a default widget_group which put's all the rest of the
        # fields in one group and renderes

        if remainder_group is None:
            remainder_group = WidgetGroup(u'')
            self.groups.append(remainder_group)
        widgets = self._get_widgets(self.form_fields.omit(
            *fields), ignore_request)
        remainder_group.widgets = widgets

        if self.widgets is None:
            self.widgets = widgets
        else:
            self.widgets += widgets


    def _get_widgets(self, form_fields, ignore_request):
        return zope.formlib.form.setUpWidgets(
            form_fields, self.prefix, self.context, self.request,
            form=self, adapters=self.adapters,
            ignore_request=ignore_request)


class AddForm(FormBase, zope.formlib.form.AddForm):
    """Add form."""

    def add(self, object):
        chooser = zope.app.container.interfaces.INameChooser(self.context)
        name = chooser.chooseName(self.suggestName(object), object)
        self.context[name] = object
        object = self.context[name]

        # Check the document out right away (if possible).
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(
            self.context[name], None)
        if manager is not None and manager.canCheckout:
            object = manager.checkout()

        self._created_object = object
        self._finished_add = True

    def suggestName(self, object):
        return object.__name__

    def nextURL(self):
        url = zope.component.getMultiAdapter(
            (self._created_object, self.request), name='absolute_url')()
        return url + '/@@edit.html'


class EditForm(FormBase, zope.formlib.form.EditForm):
    """Edit form."""

    title = "Bearbeiten"

class DisplayForm(FormBase, zope.formlib.form.PageDisplayForm):
    """Display form."""

    title = "Anzeigen"

    def _get_widgets(self, form_fields, ignore_request):
        return zope.formlib.form.setUpEditWidgets(
            form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, for_display=True,
            ignore_request=ignore_request)
