
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.workflow.interfaces
import zope.i18n
import zope.viewlet.viewlet


class Published:
    """Indicate whether an object is published or not."""

    messages = {
        'published': _('Published'),
        'not-published': _('Not published'),
        'published-with-changes': _('Published but has changes'),
    }

    def update(self):
        self.status = zeit.cms.workflow.interfaces.IPublicationStatus(
            self.context, None)

    def render(self):
        if self.status is None:
            return u''
        status = self.status.published
        if status is None:
            return u''
        title = self.messages[status]
        title = zope.i18n.translate(title, context=self.request)
        return (u'<span class="publish-state %s" title="%s"></span>' % (
            status, title))


class PublishedViewlet(Published, zope.viewlet.viewlet.ViewletBase):
    pass


class PublishedView(Published):

    def __call__(self):
        self.update()
        return self.render()
