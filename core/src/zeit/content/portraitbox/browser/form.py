# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Portraitbox forms."""

import zope.formlib.form

import zope.app.appsetup.interfaces

import gocept.form.grouped

import zeit.cms.interfaces
import zeit.cms.browser.form
import zeit.wysiwyg.interfaces
import zeit.cms.content.browser.form
from zeit.cms.i18n import MessageFactory as _

import zeit.content.portraitbox.interfaces
import zeit.content.portraitbox.portraitbox


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
            zeit.content.portraitbox.interfaces.IPortraitbox,
            zeit.cms.interfaces.ICMSContent,
            zeit.wysiwyg.interfaces.IHTMLContent).omit('text')

    field_groups = (
        gocept.form.grouped.RemainingFields(
            _('Head'),
            css_class='column-right'),
        gocept.form.grouped.Fields(
            _('Portrait'),
            ('name', 'html', 'image'),
            css_class='full-width wide-widgets'),
    )


class Add(FormBase, zeit.cms.browser.form.AddForm):

    factory = zeit.content.portraitbox.portraitbox.Portraitbox
    title = _('Add portraitbox')


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit portraitbox')
    form_fields = FormBase.form_fields.omit('__name__')


class Display(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('View portraitbox')
    form_fields = FormBase.form_fields.omit('__name__')


@zope.component.adapter(zope.app.appsetup.interfaces.IDatabaseOpenedEvent)
def register_asset_interface(event):
    zeit.cms.content.browser.form.AssetBase.add_asset_interface(
        zeit.content.portraitbox.interfaces.IPortraitboxReference)
