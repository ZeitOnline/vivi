# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component as grok
import zeit.cms.workflow.interfaces
import zeit.newsletter.interfaces
import zeit.workflow.interfaces
import zeit.workflow.publishinfo


class Workflow(zeit.workflow.publishinfo.NotPublishablePublishInfo,
               grok.Adapter):

    grok.context(zeit.newsletter.interfaces.INewsletter)
    grok.implements(zeit.newsletter.interfaces.INewsletterWorkflow)
    grok.provides(zeit.newsletter.interfaces.INewsletterWorkflow)

    zeit.cms.content.dav.mapProperties(
        zeit.newsletter.interfaces.INewsletterWorkflow,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('sent',),
        use_default=True, live=True)

    def can_publish(self):
        return True


@grok.subscribe(
    zeit.newsletter.interfaces.INewsletter,
    zeit.cms.workflow.interfaces.IPublishedEvent)
def send_email(context, event):
    info = zeit.cms.workflow.interfaces.IPublishInfo(context)
    if info.sent:
        return
    context.send()
    info.sent = True
