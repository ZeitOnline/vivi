from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import zeit.cms.browser.interfaces
import zeit.edit.browser.form
import zope.interface


class Topic(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'topic'
    undo_description = _('edit topic page')
    form_fields = FormFields(
        zeit.campus.interfaces.ITopic)

    def setUpWidgets(self, *args, **kw):
        super(Topic, self).setUpWidgets(*args, **kw)
        self.widgets['page'].detail_view_name = '@@related-details'

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(Topic, self).__call__()


class StudyCourse(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'studycourse'
    undo_description = _('edit study course')
    form_fields = FormFields(
        zeit.campus.interfaces.IStudyCourse).select('course')
