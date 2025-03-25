import gocept.selenium
import zope.app.appsetup.product
import zope.component
import zope.interface

from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR, CAN_PUBLISH_WARNING
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.connector.testing
import zeit.content.article.testing
import zeit.push.testing
import zeit.workflow.publishinfo


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'dependency-publish-limit': '100',
        'blacklist': '/blacklist',
        'publisher-base-url': 'http://localhost:8060/test/',
        'speechbert-ignore-genres': 'datenvisualisierung video quiz',
        'speechbert-ignore-templates': 'zon-liveblog',
    },
    bases=(zeit.push.testing.CONFIG_LAYER,),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(bases=(ZOPE_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(CELERY_LAYER,))

HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(name='SeleniumLayer', bases=(WD_LAYER,))

SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    features=['zeit.connector.sql'],
    bases=(CONFIG_LAYER, zeit.connector.testing.SQL_CONFIG_LAYER),
)
SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(SQL_ZCML_LAYER,))
SQL_CONNECTOR_LAYER = zeit.connector.testing.SQLDatabaseLayer(bases=(SQL_ZOPE_LAYER,))

ARTICLE_LAYER = zeit.cms.testing.AdditionalZCMLLayer(
    'zeit.content.article',
    'ctesting.zcml',
    bases=(ZOPE_LAYER, zeit.content.article.testing.CONFIG_LAYER),
)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):
    layer = WEBDRIVER_LAYER


class SQLTestCase(zeit.connector.testing.TestCase):
    layer = SQL_CONNECTOR_LAYER


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.retresco.interfaces.ITMSRepresentation)
class MockTMSRepresentation:
    result = _default_result = {}

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return self.result

    @classmethod
    def reset(cls):
        cls.result = cls._default_result


reset_mock_tms = MockTMSRepresentation.reset  # ZCA cannot use classmethods


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


def publish_json(context, name):
    data_factory = zope.component.getAdapter(
        context, zeit.workflow.interfaces.IPublisherData, name=name
    )
    return data_factory.publish_json()
