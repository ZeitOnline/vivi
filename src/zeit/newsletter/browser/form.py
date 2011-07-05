# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.edit.browser.form
import zeit.newsletter.interfaces
import zope.formlib.form


class MetadataForms(zeit.edit.browser.form.FormGroup):
    """Newsletter metadata forms."""

    title = _('Metadata')


class Metadata(zeit.edit.browser.form.InlineForm):

    legend = _('Metadata')
    prefix = 'metadata'
    undo_description = _('edit metadata')

    form_fields = zope.formlib.form.FormFields(
        zeit.newsletter.interfaces.INewsletter).select('subject')
