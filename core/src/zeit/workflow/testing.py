from mockssh.streaming import Stream, StreamTransfer
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_WARNING
import gocept.selenium
import io
import mockssh
import os
import pkg_resources
import plone.testing
import shutil
import stat
import tempfile
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
    publisher-base-url http://localhost:8060/test/
    facebooknewstab-startdate 2021-03-24
    speechbert-ignore-genres datenvisualisierung video quiz
    speechbert-ignore-templates zon-liveblog
</product-config>
"""

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config, bases=(zeit.cms.testing.CONFIG_LAYER,))


class WorkflowScriptsLayer(plone.testing.Layer):
    """Layer which copies the publish/retract scripts and makes them
    executable."""

    def setUp(self):
        self._tempfiles = []
        self['publish-script'] = self._make_copy('publish.sh')

    def tearDown(self):
        for f in self._tempfiles:
            os.remove(f.name)
        del self._tempfiles
        del self['publish-script']

    def testSetUp(self):
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        product_config['publish-script'] = self['publish-script']

    def _make_copy(self, script):
        source = pkg_resources.resource_string(
            'zeit.workflow.tests', 'fixtures/%s' % script)
        destination = tempfile.NamedTemporaryFile(suffix=script, delete=False)
        destination.write(source)
        destination.close()
        os.chmod(destination.name, stat.S_IRUSR | stat.S_IXUSR)
        self._tempfiles.append(destination)
        return destination.name


SCRIPTS_LAYER = WorkflowScriptsLayer()


class SSHServerLayer(plone.testing.Layer):

    def setUp(self):
        self['tmpdir'] = tempfile.mkdtemp()
        self['ssh-user'] = 'mockpublisher'
        self['ssh-key-path'] = self['tmpdir'] + '/mockssh.key'
        shutil.copy(
            pkg_resources.resource_filename('mockssh', 'sample-user-key'),
            self['ssh-key-path'])
        os.chmod(self['ssh-key-path'], 0o600)  # Pacify ssh client.
        self['ssh-server'] = mockssh.Server(
            {self['ssh-user']: self['ssh-key-path']})
        self['ssh-server'].__enter__()

    def testSetUp(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        config['publish-host'] = 'localhost'
        config['publish-port'] = str(self['ssh-server'].port)
        config['publish-user'] = self['ssh-user']
        config['publish-command-publish'] = 'cat'
        config['publish-command-retract'] = 'cat'
        config['publish-ssh-options'] = (
            '-i %s -o StrictHostKeyChecking=no' % self['ssh-key-path'])
        del config['publish-script']

    def tearDown(self):
        self['ssh-server'].__exit__()
        del self['ssh-server']
        shutil.rmtree(self['tmpdir'])
        del self['tmpdir']


SSH_SERVER_LAYER = SSHServerLayer()


# Work around https://github.com/carletes/mock-ssh-server/issues/24
def transfer(self):
    if self.eof:
        return None
    data = original_transfer(self)
    out = self.write.__self__
    # Kludgy way of recognizing that we're indeed handling the stdin stream
    # with the least amount of monkey-patching:
    if isinstance(out, io.BufferedWriter) and not data:
        self.eof = True
        out.close()
    return data


original_transfer = Stream.transfer
Stream.transfer = transfer
Stream.eof = False


# Prevent ResourceWarning
def run_and_close(self):
    original_run(self)
    self.process.stdin.close()
    self.process.stdout.close()
    self.process.stderr.close()


original_run = StreamTransfer.run
StreamTransfer.run = run_and_close


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(CONFIG_LAYER, SCRIPTS_LAYER))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(bases=(ZOPE_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(CELERY_LAYER,))

SSH_LAYER = plone.testing.Layer(
    bases=(ZOPE_LAYER, SSH_SERVER_LAYER), name='SSHLayer', module=__name__)

HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='SeleniumLayer', bases=(WD_LAYER,))


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
        context,
        zeit.workflow.interfaces.IPublisherData,
        name=name)
    return data_factory.publish_json()
