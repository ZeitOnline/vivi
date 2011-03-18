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


class Add(zeit.content.article.browser.recension.FormBase,
          zeit.edit.browser.view.AddBox):

    title = _('Add book information')
    form_fields = (
        zeit.content.article.browser.recension.FormBase.form_fields.omit(
            'raw_data'))
    factory = zeit.content.article.recension.BookRecension

    def add(self, obj):
        self.context.append(obj)
        # prevent redirect
        self._finished_add = False
        return obj
