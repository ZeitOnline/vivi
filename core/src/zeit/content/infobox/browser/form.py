# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import gocept.form.grouped

import zeit.cms.interfaces
import zeit.cms.browser.form
import zeit.cms.content.browser.form
from zeit.cms.i18n import MessageFactory as _

import zeit.content.infobox.interfaces
import zeit.content.infobox.infobox


class FormBase(object):

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.infobox.interfaces.IInfobox) +
        zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent))

    field_groups = (
        gocept.form.grouped.Fields(
            _('Texts'),
            ('supertitle', 'contents',),
            css_class='column-left wide-widgets'),
        gocept.form.grouped.RemainingFields(
            _('Head'),
            css_class='column-right'))


class Add(FormBase, zeit.cms.browser.form.AddForm):

    factory = zeit.content.infobox.infobox.Infobox
    title = _('Add infobox')


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit infobox')
    form_fields = FormBase.form_fields.omit('__name__')
    field_groups = (
        gocept.form.grouped.Fields(
            _('Texts'),
            ('supertitle', 'contents',),
            css_class='full-width wide-widgets'),
    )


class Display(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('View infobox')


zeit.cms.content.browser.form.AssetBase.add_asset_interface(
    zeit.content.infobox.interfaces.IInfoboxReference)
