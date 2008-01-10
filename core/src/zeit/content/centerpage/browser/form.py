# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO
import datetime

import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.cms.content.browser.interfaces
import zeit.xmleditor.browser.form

import zeit.content.centerpage.interfaces


ITemplateChooserSchema = (
    zeit.cms.content.browser.template.TemplateChooserSchema(
        'Centerpage templates'))


class ChooseTemplate(zeit.cms.content.browser.template.ChooseTemplateForm):
    """Form for choosing the article template."""

    add_view = 'zeit.content.centerpage.Add'
    form_fields = zope.formlib.form.FormFields(ITemplateChooserSchema)


class CPFormBase(object):

    field_groups = zeit.cms.browser.form.metadataFieldGroups
    form_fields = (
        zope.formlib.form.Fields(zeit.cms.interfaces.ICMSContent) +
        zope.formlib.form.Fields(
            zeit.content.centerpage.interfaces.ICenterPageMetadata))


class AddForm(CPFormBase, zeit.cms.browser.form.AddForm):

    form_fields = CPFormBase.form_fields + ChooseTemplate.form_fields

    def create(self, data):
        source = None
        template = data.get('template')
        if template:
            source = StringIO.StringIO(
                zeit.cms.content.interfaces.IXMLSource(template))
        del data['template']
        cp = zeit.content.centerpage.centerpage.CenterPage(source)
        self.applyChanges(cp, data)
        return cp

    def _get_widgets(self, form_fields, ignore_request=False):
        widgets = super(AddForm, self)._get_widgets(
            form_fields, ignore_request)

        zeit.cms.content.browser.interfaces.ITemplateWidgetSetup(
            self).setup_widgets(
                widgets, ChooseTemplate.add_view, ITemplateChooserSchema,
                ignore_request)

        return widgets


class EditForm(CPFormBase, zeit.cms.browser.form.EditForm):
    """CP edit form."""


class DisplayForm(CPFormBase, zeit.cms.browser.form.DisplayForm):

    form_fields = zope.formlib.form.Fields(
        zeit.content.centerpage.interfaces.ICenterPageMetadata,
        render_context=True, omit_readonly=False)


class XMLContainerForm(zeit.xmleditor.browser.form.FormBase):

    label = 'Container bearbeiten'

    form_fields = zope.formlib.form.Fields(
        zeit.content.centerpage.interfaces.IContainer)


class XMLColumnForm(zeit.xmleditor.browser.form.FormBase):

    label = 'Column bearbeiten'

    form_fields = zope.formlib.form.Fields(
        zeit.content.centerpage.interfaces.IColumn)

