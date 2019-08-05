from zeit.cms.content.interfaces import WRITEABLE_LIVE
import grokcore.component as grok
import zeit.cms.workflow.interfaces
import zeit.edit.rule
import zeit.newsletter.interfaces
import zeit.workflow.interfaces
import zope.session.interfaces


@grok.implementer(zeit.newsletter.interfaces.INewsletterWorkflow)
class Workflow(zeit.workflow.timebased.TimeBasedWorkflow,
               grok.Adapter):

    grok.context(zeit.newsletter.interfaces.INewsletter)
    grok.provides(zeit.newsletter.interfaces.INewsletterWorkflow)

    zeit.cms.content.dav.mapProperties(
        zeit.newsletter.interfaces.INewsletterWorkflow,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('sent',),
        use_default=True, writeable=WRITEABLE_LIVE)

    def can_publish(self):
        return zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS


@grok.subscribe(
    zeit.newsletter.interfaces.INewsletter,
    zeit.cms.workflow.interfaces.IPublishedEvent)
def send_email(context, event):
    info = zeit.cms.workflow.interfaces.IPublishInfo(context)
    if info.sent:
        return
    context.send()
    info.sent = True


@grok.implementer(zeit.newsletter.interfaces.ITestRecipient)
class TestRecipient(grok.Adapter):
    """The recipient to test sending a newsletter is pre-populated with the
    current user's email address (from LDAP), but can be overriden in the
    session.

    We need the request for all these things, so we adapt it. But since the
    workflow form has the newsletter as context which is completely irrelevant
    for us, we cheat and pretend to be an adapter ourselves (i.e. are callable
    with a context), but in fact we ignore it.
    """

    grok.context(zeit.cms.browser.interfaces.ICMSLayer)

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
        return self.request.principal.description

    @email.setter
    def email(self, value):
        self.session[self.__module__]['test-recipient'] = value
