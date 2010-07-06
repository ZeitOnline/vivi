# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import os
import os.path
import stat
import tempfile
import threading
import time
import transaction
import unittest
import zeit.cms.testing
import zeit.workflow.publish
import zope.app.testing.functional


class WorkflowLayerFactory(zope.app.testing.functional.ZCMLLayer):
    """Layer which copies the publish/retract scripts and makes them
    executable."""

    def __init__(self, *args, **kwargs):
        zope.app.testing.functional.ZCMLLayer.__init__(self, *args, **kwargs)
        self._tempfiles = []

    def setUp(self):
        zope.app.testing.functional.ZCMLLayer.setUp(self)
        product_config['publish-script'] = self._make_copy('publish.sh')
        product_config['retract-script'] = self._make_copy('retract.sh')

    def tearDown(self):
        for name in self._tempfiles:
            os.remove(name)
        zope.app.testing.functional.ZCMLLayer.tearDown(self)

    def _make_copy(self, script):
        source = os.path.join(os.path.dirname(__file__), script)
        fd, destination = tempfile.mkstemp(suffix=script)
        self._tempfiles.append(destination)
        f = os.fdopen(fd, 'w')
        f.write(open(source).read())
        f.close()
        os.chmod(destination, stat.S_IRUSR|stat.S_IXUSR)
        return destination


WorkflowLayer = WorkflowLayerFactory(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'WorkflowLayer', allow_teardown=True)


product_config = {
    'path-prefix': 'work',
    'news-channel': 'http://xml.zeit.de/politik.feed',
}


class FakePublishTask(zeit.workflow.publish.PublishRetractTask):

    def __init__(self):
        self.test_log = []

    def run(self, obj, info):
        time.sleep(0.1)
        self.test_log.append((obj, info))


class PublishRetractLockingTest(zeit.cms.testing.FunctionalTestCase):

    layer = WorkflowLayer
    product_config = product_config

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
        layer=WorkflowLayer,
        product_config={'zeit.workflow': product_config}))
    suite.addTest(unittest.makeSuite(PublishRetractLockingTest))
    return suite
