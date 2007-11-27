# Copyright (c) 2006-2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form
import zope.formlib.interfaces

import zope.app.container.interfaces

import gocept.form.grouped

import zeit.cms.checkout.interfaces
from zeit.cms.i18n import MessageFactory as _


REMAINING_FIELDS = object()


metadataFieldGroups = (
    gocept.form.grouped.Fields(
        _("Navigation"),
        ('navigation', 'keywords', 'serie'),
        css_class='small-and-tall'),
    gocept.form.grouped.Fields(
        _("Kopf"),
        ('year', 'volume', 'page', 'ressort'),
        css_class='medium-float'),
    gocept.form.grouped.Fields(
        _("Optionen"),
        ('dailyNewsletter', 'boxMostRead', 'commentsAllowed', 'banner'),
        css_class='medium-float'),
    gocept.form.grouped.RemainingFields(
        _("Texte"),
        css_class='column-left'),
    gocept.form.grouped.Fields(
        _("sonstiges"),
        ('authors', 'copyrights', 'pageBreak', 'automaticTeaserSyndication',
         'images'),
        css_class= 'column-right'),
    )

class FormBase(object):

    widget_groups = ()

    def applyChanges(self, object, data):
        return zope.formlib.form.applyChanges(
            object, self.form_fields, data, self.adapters)

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
    factory = None

    def create(self, data):
        if self.factory is None:
            raise ValueError("No factory specified.")
        new_object = self.factory()
        self.applyChanges(new_object, data)
        return new_object

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

    def setUpWidgets(self, ignore_request=False):
        if not ignore_request:
            form = self.request.form
            if not form:
                form['form.year'] = str(datetime.datetime.now().year)
                form['form.volume'] = str(int(  # Strip leading 0
                    datetime.datetime.now().strftime('%W')))
        super(AddForm, self).setUpWidgets(ignore_request)


class EditForm(FormBase, gocept.form.grouped.EditForm):
    """Edit form."""

    title = _("Edit")


class DisplayForm(FormBase, gocept.form.grouped.DisplayForm):
    """Display form."""

    title = _("View")
