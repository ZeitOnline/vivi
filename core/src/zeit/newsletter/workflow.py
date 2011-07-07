# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component as grok
import zeit.cms.workflow.interfaces
import zeit.newsletter.interfaces
import zeit.workflow.interfaces
import zeit.workflow.publishinfo
import zope.interface
import zope.session.interfaces


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


class TestRecipient(object):
    """The recipient to test sending a newsletter is pre-populated with the
    current user's email address (from LDAP), but can be overriden in the
    session.

    Since the workflow form has the newsletter as context which is completely
    irrelevant for us, we cheat and pretend to be an adapter (i.e. are callable
    with a context), but in fact we ignore it.
    """

    zope.interface.implements(zeit.newsletter.interfaces.ITestRecipient)

    def __init__(self, request):
        self.request = request

    def __call__(self, context):
        return self

    @property
    def session(self):
        return zope.session.interfaces.ISession(self.request)

    @property
    def email(self):
        return self.session[self.__module__].get(
            'test-recipient', self.get_email_for_principal())

    def get_email_for_principal(self):
        return 'default from LDAP not yet implemented' # XXX see #9234

    @email.setter
    def email(self, value):
        self.session[self.__module__]['test-recipient'] = value
