# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import lovely.remotetask.interfaces
import zeit.cms.browser.menu
import zeit.cms.workflow.interfaces
import zope.component


class PublishMenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):

    sort = -1
    lightbox = '@@publish.html'

    def render(self):
        return super(PublishMenuItem, self).render()


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


class RetractMenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):

    sort = -1
    lightbox = '@@retract.html'

    @property
    def visible(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return info.published

    def render(self):
        if self.visible:
            return super(RetractMenuItem, self).render()
        else:
            return ''
