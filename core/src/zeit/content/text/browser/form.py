# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Plain text forms."""

import zope.formlib.form

import zeit.cms.browser.form
import zeit.content.text.interfaces
import zeit.content.text.text
from zeit.cms.i18n import MessageFactory as _


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.text.interfaces.IText)


class Add(FormBase,
          zeit.cms.browser.form.AddForm):
    """Add plain text."""

    title = _('Add plain text')
    factory = zeit.content.text.text.Text


class Edit(FormBase,
           zeit.cms.browser.form.EditForm):
    """Edit plain text."""

    title = _('Edit plain text')


class Display(FormBase,
              zeit.cms.browser.form.DisplayForm):
    """View plain text."""

    title = _('View plain text')
