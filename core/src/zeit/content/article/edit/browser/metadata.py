# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.content.article.edit.browser.form
import zope.formlib.form
import zope.formlib.interfaces


class Metadata(object):
    """metadata forms view."""

    title = _('Metadata')


class Head(zeit.content.article.edit.browser.form.InlineForm):

    legend = _('Head')
    prefix = 'head'
    undo_description = _('edit metadata (head)')
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'ressort', 'sub_ressort', 'keywords', 'product_id',
            'dailyNewsletter')

    def render(self):
        result = super(Head, self).render()
        if result:
            result += (
                '<script type="text/javascript">'
                '    zeit.cms.configure_ressort_dropdown("%s.");'
                '</script>') % (self.prefix,)
        return result
