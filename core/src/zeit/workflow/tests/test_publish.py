# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import threading
import time
import transaction
import zeit.cms.testing
import zeit.workflow.publish
import zeit.workflow.testing


class FakePublishTask(zeit.workflow.publish.PublishRetractTask):

    def __init__(self):
        self.test_log = []

    def run(self, obj, info):
        time.sleep(0.1)
        self.test_log.append((obj, info))


class PublishRetractLockingTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.WorkflowLayer

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
        import zope.component
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
