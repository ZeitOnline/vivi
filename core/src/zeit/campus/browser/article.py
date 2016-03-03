from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.form import FormFields
import zeit.cms.browser.interfaces
import zeit.edit.browser.form
import zope.interface


class TopicpageLink(zeit.edit.browser.form.InlineForm):

    legend = ''
    prefix = 'topicpagelink'
    undo_description = _('edit topicpage link')
    form_fields = FormFields(
        zeit.magazin.interfaces.ITopicpageLink)

    def setUpWidgets(self, *args, **kw):
        super(TopicpageLink, self).setUpWidgets(*args, **kw)
        self.widgets['topicpagelink'].detail_view_name = '@@related-details'

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(TopicpageLink, self).__call__()
