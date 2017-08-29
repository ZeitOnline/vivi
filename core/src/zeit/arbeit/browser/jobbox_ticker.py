from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.interfaces
import zeit.edit.browser.form
import zope.formlib.form
import zope.interface
import zeit.arbeit.interfaces


class JobboxTicker(zeit.edit.browser.form.InlineForm):

    legend = ''
    undo_description = _('edit jobbox ticker')
    form_fields = zope.formlib.form.FormFields(
        zeit.arbeit.interfaces.IJobboxTicker).select('jobbox')

    @property
    def prefix(self):
        return 'jobboxticker.{0}'.format(self.context.__name__)
