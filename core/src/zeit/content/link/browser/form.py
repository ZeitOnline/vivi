# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Link forms."""

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.browser.form
import zeit.content.link.interfaces
import zeit.content.link.link
import zope.formlib.form


class Base(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.link.interfaces.ILink).omit('xml', 'authors')


class Add(Base, zeit.cms.content.browser.form.CommonMetadataAddForm):

    title = _('Add link')
    factory = zeit.content.link.link.Link
    form_fields = Base.form_fields.omit(
        'automaticMetadataUpdateDisabled')


class Edit(Base, zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _('Edit link')


class Display(Base, zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _('View link metadata')
