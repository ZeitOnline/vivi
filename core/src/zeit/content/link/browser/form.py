# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import zeit.cms.browser.form
from zeit.cms.i18n import MessageFactory as _

import zeit.content.link.interfaces
import zeit.content.link.link


class Base(object):

    field_groups = zeit.cms.browser.form.metadataFieldGroups

    form_fields = (
        zope.formlib.form.FormFields(zeit.content.link.interfaces.ILink) +
        zope.formlib.form.FormFields(
            zeit.cms.content.interfaces.ICommonMetadata) +
        zope.formlib.form.FormFields(zeit.cms.interfaces.ICMSContent) +
        zope.formlib.form.FormFields(zeit.content.image.interfaces.IImages))


class Add(Base, zeit.cms.browser.form.AddForm):

    title = _('Add link')
    factory = zeit.content.link.link.Link
    checkout = False

class Edit(Base, zeit.cms.browser.form.EditForm):

    title = _('Edit link')


class Display(Base, zeit.cms.browser.form.DisplayForm):

    title = _('View link metadata')
