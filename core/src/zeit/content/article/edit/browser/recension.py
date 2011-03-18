# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.content.article.browser.recension


class RecensionForms(object):
    """Article recension forms."""

    title = _('Recensions')


class Edit(zeit.content.article.browser.recension.FormBase,
           zeit.edit.browser.view.EditBox):

    title = _('Edit book information')
    field_groups = (
        zeit.content.article.browser.recension.FormBase.field_groups) + (
        gocept.form.grouped.RemainingFields(
            _('Raw data'),
            css_class='fullWidth'),)
