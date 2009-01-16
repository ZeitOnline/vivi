# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Workflow indicators."""

import zope.component
import zope.dublincore.interfaces
import zope.i18n
import zope.viewlet.viewlet

import zeit.cms.workflow
from zeit.cms.i18n import MessageFactory as _


class Published(zope.viewlet.viewlet.ViewletBase):
    """Indicate whether an object is published or not."""

    def update(self):
        self.publish_info = zeit.cms.workflow.interfaces.IPublishInfo(
            self.context, None)

    def render(self):
        if self.publish_info is None:
            return u''
        times = zope.dublincore.interfaces.IDCTimes(self.context)
        if self.publish_info.published:
            if (not times.modified
                or not self.publish_info.date_last_published
                or (self.publish_info.date_last_published >
                     times.modified)):
                img = 'published'
                title = _('Published')
            else:
                img = 'published-with-changes'
                title = _('Published but has changes')
        else:
            img = 'not-published'
            title = _('Not published')

        title = zope.i18n.translate(title, context=self.request)
        cms_resources= zope.component.getAdapter(
            self.request, name='zeit.cms')
        return (u'<img class="publish-state" src="%s/icons/%s.png" title="%s" '
                '/>' % (cms_resources(), img, title))
