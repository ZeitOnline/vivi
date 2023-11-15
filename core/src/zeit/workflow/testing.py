from unittest import mock
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_WARNING
import gocept.selenium
import plone.testing
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.workflow.publishinfo
import zope.app.appsetup.product
import zope.component
import zope.interface


product_config = """
<product-config zeit.workflow>
    dependency-publish-limit 100
    blacklist /blacklist
    publisher-base-url http://localhost:8060/test/
    facebooknewstab-startdate 2021-03-24
    speechbert-ignore-genres datenvisualisierung video quiz
    speechbert-ignore-templates zon-liveblog
</product-config>
"""

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.cms.testing.CONFIG_LAYER,)
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(bases=(ZOPE_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(CELERY_LAYER,))

HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(name='SeleniumLayer', bases=(WD_LAYER,))


class TMSMockLayer(plone.testing.Layer):
    def testSetUp(self):
        self.patch = mock.patch('zeit.retresco.interfaces.ITMSRepresentation')
        self.representation = self.patch.start()

    def testTearDown(self):
        self.patch.stop()


TMS_MOCK_LAYER = TMSMockLayer(name='TMSMockLayer', bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER


@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublishInfo)
class FakeValidatingWorkflow(zeit.workflow.publishinfo.PublishInfo):
    """Workflow with validations like zeit.edit.rule.ValidatingWorkflow.

    Just returns the data fed into __init__ as validation info.

    We cannot use the Workflow from zeit.edit, since zeit.edit depends on
    zeit.cms. Therefore we use a fake workflow here, to test the abstract
    mechanism to display validation errors during publish.

    """

    def __init__(self, context, message, can_publish):
        self.context = context
        self.error_messages = [message]
        self._can_publish = can_publish

    def can_publish(self):
        return self._can_publish


@zope.component.adapter(zeit.cms.testcontenttype.interfaces.IExampleContentType)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublishInfo)
def workflow_with_error_for_testcontent(context):
    return FakeValidatingWorkflow(context, 'Fake Validation Error Message', CAN_PUBLISH_ERROR)


@zope.component.adapter(zeit.cms.testcontenttype.interfaces.IExampleContentType)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublishInfo)
def workflow_with_warning_for_testcontent(context):
    return FakeValidatingWorkflow(context, 'Fake Validation Warning Message', CAN_PUBLISH_WARNING)


class FakeValidatingWorkflowMixin:
    """Mixin to register and unregister FakeValidatingWorkflow."""

    def setUp(self):
        super().setUp()
        self.registered_adapters = []

    def tearDown(self):
        super().tearDown()
        gsm = zope.component.getGlobalSiteManager()
        for adapter in self.registered_adapters:
            gsm.unregisterAdapter(adapter)

    def register_workflow_with_error(self):
        self._register_workflow(workflow_with_error_for_testcontent)

    def register_workflow_with_warning(self):
        self._register_workflow(workflow_with_warning_for_testcontent)

    def _register_workflow(self, workflow):
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerAdapter(workflow)
        self.registered_adapters.append(workflow)


def run_tasks():
    """For browser tests: Wait for already enqueued publish job, by running
    another job; since we only have on worker, this works out fine.
    Unfortunately we have to mimic the DAV-cache race condition workaround here
    too and wait an additional 5 seconds, sigh.
    """
    zeit.cms.testing.celery_ping.apply_async(countdown=5).get()


def publish_json(context, name):
    data_factory = zope.component.getAdapter(
        context, zeit.workflow.interfaces.IPublisherData, name=name
    )
    return data_factory.publish_json()
