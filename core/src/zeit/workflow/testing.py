# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
import logging
import lovely.remotetask.interfaces
import os
import sys
import zeit.cms.testing
import zope.component


product_config = """
<product-config zeit.workflow>
    path-prefix work
</product-config>
"""

WorkflowBaseLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class WorkflowScriptsLayer(object):
    """Layer which copies the publish/retract scripts and makes them
    executable."""

    @classmethod
    def setUp(cls):
        import zope.app.appsetup.product
        cls._tempfiles = []
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        product_config['publish-script'] = cls._make_copy('publish.sh')
        product_config['retract-script'] = cls._make_copy('retract.sh')

    @classmethod
    def tearDown(cls):
        for f in cls._tempfiles:
            os.remove(f.name)
        del cls._tempfiles

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass

    @classmethod
    def _make_copy(cls, script):
        import os
        import pkg_resources
        import stat
        import tempfile
        source = pkg_resources.resource_string(__name__, script)
        destination = tempfile.NamedTemporaryFile(suffix=script, delete=False)
        destination.write(source)
        destination.close()
        os.chmod(destination.name, stat.S_IRUSR|stat.S_IXUSR)
        cls._tempfiles.append(destination)
        return destination.name


class WorkflowLayer(WorkflowBaseLayer, WorkflowScriptsLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


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
