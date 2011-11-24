# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Link forms."""

import zope.formlib.form

import zeit.cms.browser.form
from zeit.cms.i18n import MessageFactory as _

import zeit.content.link.interfaces
import zeit.content.link.link
import zeit.cms.content.browser.form


class Base(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.link.interfaces.ILink).omit('xml')


class Add(Base, zeit.cms.content.browser.form.CommonMetadataAddForm):

    title = _('Add link')
    factory = zeit.content.link.link.Link
    form_fields = Base.form_fields.omit(
        'automaticMetadataUpdateDisabled')


class Edit(Base, zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _('Edit link')


class Display(Base, zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _('View link metadata')
