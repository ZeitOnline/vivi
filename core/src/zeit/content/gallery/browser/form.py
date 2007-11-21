# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.content.gallery.interfaces
import zeit.content.gallery.gallery


class FormBase(object):

    form_fields = (
        zope.formlib.form.Fields(
            zeit.cms.interfaces.ICMSContent,
            omit_readonly=False).omit('uniqueId') +
        zope.formlib.form.Fields(
            zeit.content.gallery.interfaces.IGalleryMetadata,
            omit_readonly=False))

    field_groups = zeit.cms.browser.form.metadataFieldGroups

class AddForm(FormBase, zeit.cms.browser.form.AddForm):

    title = _("Add gallery")
    factory = zeit.content.gallery.gallery.Gallery


class EditForm(FormBase, zeit.cms.browser.form.EditForm):

    title = _("Edit Gallery")
    form_fields = FormBase.form_fields.omit('__name__')


class DisplayForm(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _("Gallery")
