import kombu
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_WARNING
import gocept.httpserverlayer.wsgi
import gocept.selenium
import logging
import os
import pkg_resources
import plone.testing
import stat
import tempfile
import z3c.celery.conftest
import z3c.celery.layer
import z3c.celery.testing
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


CELERY_QUEUES = (
    'default', 'publish_homepage', 'publish_highprio', 'publish_default',
    'publish_lowprio', 'publish_timebased')
ADDITIONAL_CELERY_CONFIG = {
    'task_track_started': True,
    'task_routes': ('zeit.cms.celery.route_task',),
    'task_default_queue': 'default',
    'task_queues': [kombu.Queue(q) for q in CELERY_QUEUES],
    'QUEUENAMES': {q: q for q in CELERY_QUEUES}
}


class CelerySettingsLayer(plone.testing.Layer):
    """Settings for the Celery end to end tests."""

    def __init__(self, product_config):
        super(CelerySettingsLayer, self).__init__()
        self.product_config = product_config

    def setUp(self):
        # Maybe we also want to truncate this file in future for test isolation
        self['storage_file_fixture'] = z3c.celery.conftest.storage_file()
        self['zodb_path'] = next(self['storage_file_fixture'])
        self['zope_conf_name'] = self.create_zope_conf(self['zodb_path'])

        self['celery_config'] = z3c.celery.conftest.celery_config(
            self['zope_conf_name'])
        self['celery_config'].update(ADDITIONAL_CELERY_CONFIG)
        self['celery_parameters'] = z3c.celery.conftest.celery_parameters()
        self['celery_worker_parameters'] = {'queues': CELERY_QUEUES}
        self['celery_includes'] = ['zeit.workflow.publish']

        self['logfile_name'] = self.create_temp_file()
        self['log_hander'] = logging.FileHandler(self['logfile_name'])
        logging.root.addHandler(self['log_hander'])

    def create_temp_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            return tmpfile.name

    def create_zope_conf(self, storage_file_name):
        self['publish-script-path'] = self.create_temp_file()
        with open(self['publish-script-path'], 'w') as f:
            f.write('#!/bin/sh\nexit 0')
        os.chmod(self['publish-script-path'], 0o755)
        self.product_config = self.product_config.replace(
            'publish-script true', 'publish-script {}'.format(
                self['publish-script-path']))
        with tempfile.NamedTemporaryFile(delete=False) as conf:
            conf.write(z3c.celery.testing.ZOPE_CONF_TEMPLATE.format(
                zodb_path=storage_file_name,
                product_config=self.product_config,
                ftesting_path=pkg_resources.resource_filename(
                    'zeit.workflow', 'ftesting.zcml')))
            conf.flush()
            return conf.name

    def testSetUp(self):
        with open(self['logfile_name'], 'w') as logfile:
            logfile.seek(0)
            logfile.truncate(0)

    def tearDown(self):
        os.unlink(self['zope_conf_name'])
        del self['zope_conf_name']
        del self['zodb_path']
        next(self['storage_file_fixture'], None)
        del self['storage_file_fixture']
        del self['celery_config']
        del self['celery_includes']
        del self['celery_parameters']
        del self['celery_worker_parameters']
        logging.root.removeHandler(self['log_hander'])
        del self['log_hander']
        os.unlink(self['publish-script-path'])
        del self['publish-script-path']
        os.unlink(self['logfile_name'])
        del self['logfile_name']


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)
CELERY_SETTINGS_LAYER = CelerySettingsLayer(ZCML_LAYER.product_config)
CONFIGURED_END_TO_END_LAYER = z3c.celery.layer.EndToEndLayer(
    bases=[CELERY_SETTINGS_LAYER], name="ConfiguredEndToEndLayer")
ZEIT_CELERY_END_TO_END_LAYER = plone.testing.Layer(
    bases=(CONFIGURED_END_TO_END_LAYER, ZCML_LAYER),
    name="ZeitCeleryEndToEndLayer")


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


WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(LAYER,))
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
