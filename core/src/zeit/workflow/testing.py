from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
import gocept.httpserverlayer.wsgi
import gocept.selenium
import logging
import lovely.remotetask.interfaces
import os
import plone.testing
import sys
import threading
import zeit.cms.testing
import zope.component


product_config = """
<product-config zeit.workflow>
    path-prefix work
    # WorkflowScriptsLayer overrides these anyway, but we provide some defaults
    # so other packages simply add our product_config for their tests.
    publish-script true
    retract-script true
    dependency-publish-limit 100
</product-config>
"""

ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class WorkflowScriptsLayer(plone.testing.Layer):
    """Layer which copies the publish/retract scripts and makes them
    executable."""

    def setUp(self):
        import zope.app.appsetup.product
        self._tempfiles = []
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        product_config['publish-script'] = self._make_copy('publish.sh')
        product_config['retract-script'] = self._make_copy('retract.sh')

    def tearDown(self):
        for f in self._tempfiles:
            os.remove(f.name)
        del self._tempfiles

    def testSetUp(self):
        pass

    def testTearDown(self):
        pass

    def _make_copy(self, script):
        import os
        import pkg_resources
        import stat
        import tempfile
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


class RemoteTaskHelper(object):

    def start_tasks(self):
        self.tasks = []
        with zeit.cms.testing.site(self.getRootFolder()):
            for name, task in zope.component.getUtilitiesFor(
                lovely.remotetask.interfaces.ITaskService):
                task.startProcessing()
                self.tasks.append(task)

    def stop_tasks(self):
        for task in self.tasks:
            task.stopProcessing()
            self._join_thread(task)

    def _join_thread(self, task):
        # XXX it would be nice if TaskService offered an API to do this
        for thread in threading.enumerate():
            if thread.getName() == task._threadName():
                thread.join()


def run_publish(priorities=(PRIORITY_DEFAULT,)):
    handler = logging.StreamHandler(sys.stdout)
    logging.root.addHandler(handler)
    oldlevel = logging.root.level
    logging.root.setLevel(logging.ERROR)
    if isinstance(priorities, str):
        priorities = [priorities]
    for priority in priorities:
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, priority)
        tasks.process()
    logging.root.removeHandler(handler)
    logging.root.setLevel(oldlevel)
