# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.content.article.edit.interfaces
import zope.formlib.form


class EditImage(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IImage).select(
            'layout', 'custom_caption')
    undo_description = _('edit image')

    @property
    def prefix(self):
        return 'form.divison.{0}'.format(self.context.__name__)
