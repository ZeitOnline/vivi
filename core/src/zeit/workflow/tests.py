# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import pkg_resources
import stat
import tempfile
import threading
import time
import transaction
import unittest
import zeit.cms.testing
import zeit.workflow.publish
import zope.app.testing.functional

product_config = """
<product-config zeit.workflow>
    path-prefix work
    news-channel http://xml.zeit.de/politik.feed
</product-config>
"""

WorkflowBaseLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config )


class WorkflowScriptsLayer(object):
    """Layer which copies the publish/retract scripts and makes them
    executable."""

    @classmethod
    def setUp(cls):
        cls._tempfiles = []
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        product_config['publish-script'] = cls._make_copy('publish.sh')
        product_config['retract-script'] = cls._make_copy('retract.sh')

    @classmethod
    def tearDown(cls):
        del cls._tempfiles


    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass

    @classmethod
    def _make_copy(cls, script):
        source = pkg_resources.resource_string(__name__, script)
        destination = tempfile.NamedTemporaryFile(suffix=script)
        destination.write(source)
        destination.flush()
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


class FakePublishTask(zeit.workflow.publish.PublishRetractTask):

    def __init__(self):
        self.test_log = []

    def run(self, obj, info):
        time.sleep(0.1)
        self.test_log.append((obj, info))


class PublishRetractLockingTest(zeit.cms.testing.FunctionalTestCase):

    layer = WorkflowLayer

    def setUp(self):
        super(PublishRetractLockingTest, self).setUp()
        self.obj = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        self.desc = zeit.workflow.publish.TaskDescription(self.obj)
        self.task = FakePublishTask()

    def run_task_in_thread(self, i, desc):
        zeit.cms.testing.set_site(self.getRootFolder())
        zeit.cms.testing.create_interaction()
        self.task(None, i, desc)
        transaction.abort()

    def test_simple(self):
        self.task(None, 1, self.desc)
        self.assertEquals(1, len(self.task.test_log))

    def test_parallel_with_same_obj(self):
        t1 = threading.Thread(
            target=self.run_task_in_thread, args=(1, self.desc))
        t2 = threading.Thread(
            target=self.run_task_in_thread, args=(2, self.desc))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertEquals(1, len(self.task.test_log))
        log = list(zope.component.getUtility(
            zeit.objectlog.interfaces.IObjectLog).get_log(self.obj))
        self.assertEquals(1, len(log))
        self.assertEquals(
            u'A publish/retract job is already active. Aborting',
            log[0].message)

    def test_parallel_with_differnt_obj(self):
        t1 = threading.Thread(
            target=self.run_task_in_thread, args=(1, self.desc))
        desc = zeit.workflow.publish.TaskDescription(
            zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/politik.feed'))
        t2 = threading.Thread(
            target=self.run_task_in_thread, args=(2, desc))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertEquals(2, len(self.task.test_log))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'autosynd.txt',
        'dependency.txt',
        'syndication.txt',
        layer=WorkflowLayer))
    suite.addTest(unittest.makeSuite(PublishRetractLockingTest))
    return suite
