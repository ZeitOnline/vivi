# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.form.grouped
import zope.formlib.form

import zeit.content.rawxml.interfaces
import zeit.content.rawxml.rawxml
from zeit.content.rawxml.i18n import MessageFactory as _


class Base(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.rawxml.interfaces.IRawXML)
    field_groups = (
        gocept.form.grouped.Fields(
            _('Raw XML'),
            ('__name__', 'title', 'xml'), ''),)


class Add(Base,
          zeit.cms.browser.form.AddForm):
    """Add raw xml."""

    factory = zeit.content.rawxml.rawxml.RawXML
    title = _('Add Raw XML')


class Edit(Base,
           zeit.cms.browser.form.EditForm):

    title = _('Edit Raw XML')


class Display(Base,
              zeit.cms.browser.form.DisplayForm):

    title = _('View Raw XML')
