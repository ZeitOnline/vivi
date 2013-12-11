# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import zeit.edit.browser.form


class EditTemplate(zeit.edit.browser.form.InlineForm):

    legend = _('ZEITmagazin ONLINE')
    prefix = 'options-zmo'
    undo_description = _('edit options')
    form_fields = FormFields(
        zeit.magazin.interfaces.IArticleTemplateSettings).select(
        'template', 'header_layout')
