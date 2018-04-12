from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_WARNING
import celery.contrib.pytest
import celery.contrib.testing.app
import celery.contrib.testing.worker
import gocept.httpserverlayer.wsgi
import gocept.selenium
import kombu
import mock
import os
import pkg_resources
import plone.testing
import stat
import tempfile
import z3c.celery.celery
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.workflow.publishinfo
import zope.app.appsetup.product
import zope.component
import zope.interface


product_config = """
<product-config zeit.workflow>
    path-prefix work
    # WorkflowScriptsLayer overrides these anyway, but we provide some defaults
    # so other packages simply add our product_config for their tests.
    publish-script true
    retract-script true
    dependency-publish-limit 100
    blacklist /blacklist
</product-config>
"""

ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class WorkflowScriptsLayer(plone.testing.Layer):
    """Layer which copies the publish/retract scripts and makes them
    executable."""

    def setUp(self):
        self._tempfiles = []
        self['publish-script'] = self._make_copy('publish.sh')
        self['retract-script'] = self._make_copy('retract.sh')

    def tearDown(self):
        for f in self._tempfiles:
            os.remove(f.name)
        del self._tempfiles
        del self['publish-script']
        del self['retract-script']

    def testSetUp(self):
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        product_config['publish-script'] = self['publish-script']
        product_config['retract-script'] = self['retract-script']

    def _make_copy(self, script):
        source = pkg_resources.resource_string(__name__, script)
        destination = tempfile.NamedTemporaryFile(suffix=script, delete=False)
        destination.write(source)
        destination.close()
        os.chmod(destination.name, stat.S_IRUSR | stat.S_IXUSR)
        self._tempfiles.append(destination)
        return destination.name

SCRIPTS_LAYER = WorkflowScriptsLayer()


LAYER = plone.testing.Layer(
    name='Layer', module=__name__, bases=(ZCML_LAYER, SCRIPTS_LAYER))
CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(
    name='CeleryLayer', bases=(LAYER,))


WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(CELERY_LAYER,))
HTTP_LAYER = gocept.httpserverlayer.wsgi.Layer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = gocept.selenium.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
SELENIUM_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='SeleniumLayer', bases=(WD_LAYER,))


class FakeValidatingWorkflow(zeit.workflow.publishinfo.PublishInfo):
    """Workflow with validations like zeit.edit.rule.ValidatingWorkflow.

    Just returns the data fed into __init__ as validation info.

    We cannot use the Workflow from zeit.edit, since zeit.edit depends on
    zeit.cms. Therefore we use a fake workflow here, to test the abstract
    mechanism to display validation errors during publish.

    """

    zope.interface.implements(
        zeit.cms.workflow.interfaces.IPublishInfo)

    def __init__(self, context, message, can_publish):
        self.context = context
        self.error_messages = [message]
        self._can_publish = can_publish

    def can_publish(self):
        return self._can_publish


@zope.component.adapter(
    zeit.cms.testcontenttype.interfaces.IExampleContentType)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublishInfo)
def workflow_with_error_for_testcontent(context):
    return FakeValidatingWorkflow(
        context, 'Fake Validation Error Message', CAN_PUBLISH_ERROR)


@zope.component.adapter(
    zeit.cms.testcontenttype.interfaces.IExampleContentType)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublishInfo)
def workflow_with_warning_for_testcontent(context):
    return FakeValidatingWorkflow(
        context, 'Fake Validation Warning Message', CAN_PUBLISH_WARNING)


class FakeValidatingWorkflowMixin(object):
    """Mixin to register and unregister FakeValidatingWorkflow."""

    def setUp(self):
        super(FakeValidatingWorkflowMixin, self).setUp()
        self.registered_adapters = []

    def tearDown(self):
        super(FakeValidatingWorkflowMixin, self).tearDown()
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
