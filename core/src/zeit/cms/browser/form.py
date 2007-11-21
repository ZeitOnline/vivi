# Copyright (c) 2006-2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form
import zope.formlib.interfaces

import zope.app.container.interfaces

import gocept.form.grouped

import zeit.cms.checkout.interfaces
from zeit.cms.i18n import MessageFactory as _


REMAINING_FIELDS = object()


class WidgetGroup(object):

    widgets = None

    def __init__(self, title, css_class=None):
        self.title = title
        self.css_class = css_class


class FormBase(object):

    widget_groups = ()


    def setUpWidgets(self, ignore_request=False):
        if self.widget_groups:
            self._convert_to_fieldgroups()
        super(FormBase, self).setUpWidgets(ignore_request)

    def _convert_to_fieldgroups(self):
        """Convert old widget_group to gocept.form's field_groups.

        This is there so we don't need to manualle rewrite all the forms. Once
        all forms have been changed this code can be removed of course.

        """
        field_groups = []

        for title, field_names, css_class in self.widget_groups:
            if field_names is REMAINING_FIELDS:
                group = gocept.form.grouped.RemainingFields(
                    title, css_class)
            else:
                group = gocept.form.grouped.Fields(
                    title, field_names, css_class)
            field_groups.append(group)
        self.field_groups = field_groups


class AddForm(FormBase, gocept.form.grouped.AddForm):
    """Add form."""

    _checked_out = False

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
            self._checked_out = True

        self._created_object = object
        self._finished_add = True

    def suggestName(self, object):
        return object.__name__

    def nextURL(self):
        if self._checked_out:
            view = 'edit.html'
        else:
            view = 'view.html'
        url = zope.component.getMultiAdapter(
            (self._created_object, self.request), name='absolute_url')()
        return '%s/@@%s' % (url, view)


class EditForm(FormBase, gocept.form.grouped.EditForm):
    """Edit form."""

    title = _("Edit")


class DisplayForm(FormBase, gocept.form.grouped.DisplayForm):
    """Display form."""

    title = _("View")
