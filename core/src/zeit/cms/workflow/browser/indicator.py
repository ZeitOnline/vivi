# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Workflow indicators."""

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.workflow.interfaces
import zope.component
import zope.i18n
import zope.viewlet.viewlet


class Published(zope.viewlet.viewlet.ViewletBase):
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
        cms_resources= zope.component.getAdapter(
            self.request, name='zeit.cms')
        return (u'<img class="publish-state" src="%s/icons/%s.png" title="%s" '
                '/>' % (cms_resources(), status, title))
