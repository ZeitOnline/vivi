# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.content.centerpage.interfaces


class CPFormBase(object):

    widget_groups = (
        (u"Kopf", ('year', 'volume', 'page', 'ressort'), 'medium-float'),
        (u"Texte", zeit.cms.browser.form.REMAINING_FIELDS, 'column-left'),
        (u"sonstiges", ('authors', 'copyrights', ), 'column-right'),
    )


class AddForm(CPFormBase, zeit.cms.browser.form.AddForm):

    form_fields = (
        zope.formlib.form.Fields(
            zeit.cms.interfaces.ICMSContent,
            omit_readonly=False).omit('uniqueId') +
        zope.formlib.form.Fields(
            zeit.content.centerpage.interfaces.ICenterPageMetadata,
            omit_readonly=False))

    def setUpWidgets(self, ignore_request=False):
        if not ignore_request:
            form = self.request.form
            if not form:
                form['form.year'] = str(datetime.datetime.now().year)
                form['form.volume'] = str(int(  # Strip leading 0
                    datetime.datetime.now().strftime('%W')))
        super(AddForm, self).setUpWidgets(ignore_request)

    def create(self, data):
        return zeit.content.centerpage.centerpage.CenterPage(**data)


class EditForm(CPFormBase, zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.Fields(
        zeit.content.centerpage.interfaces.ICenterPageMetadata,
        render_context=True, omit_readonly=False)


class DisplayForm(CPFormBase, zeit.cms.browser.form.DisplayForm):

    form_fields = zope.formlib.form.Fields(
        zeit.content.centerpage.interfaces.ICenterPageMetadata,
        render_context=True, omit_readonly=False)
