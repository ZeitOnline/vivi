# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import zeit.cms.interfaces
import zeit.cms.browser.form
from zeit.cms.i18n import MessageFactory as _

import zeit.content.infobox.interfaces
import zeit.content.infobox.infobox


class FormBase(object):

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.infobox.interfaces.IInfobox) +
        zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent))


class Add(FormBase, zeit.cms.browser.form.AddForm):

    factory = zeit.content.infobox.infobox.Infobox
    title = _('Add infobox')


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit infobox')


class Display(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('View infobox')
