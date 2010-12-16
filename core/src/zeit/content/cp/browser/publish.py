# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import lovely.remotetask.interfaces
import zc.resourcelibrary
import zeit.cms.browser.menu
import zeit.cms.checkout.interfaces
import zeit.cms.workflow.interfaces
import zope.component


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):

    sort = -1
    lightbox = '@@publish.html'

    def is_visible(self):
        manager = zeit.cms.checkout.interfaces.ICheckinManager(self.context)
        return manager.canCheckin

    # XXX duplicated from zeit.cms.checkout.browser.MenuItem
    def render(self):
        if self.is_visible():
            zc.resourcelibrary.need('zeit.content.cp.publish')
            return super(MenuItem, self).render()
        return ''


class Publish(object):

    def can_publish(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return info.can_publish()


class FlashPublishErrors(zeit.cms.browser.view.Base):

    def __call__(self, job):
        job = int(job)
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, name='general')
        if tasks.getStatus(job) != lovely.remotetask.interfaces.COMPLETED:
            return
        error = tasks.getResult(job)
        if error is not None:
            self.send_message(error, type='error')
