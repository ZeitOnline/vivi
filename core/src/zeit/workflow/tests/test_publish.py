# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import datetime
from zeit.cms.checkout.helper import checked_out
from zeit.cms.related.interfaces import IRelatedContent
from zeit.cms.testcontenttype.testcontenttype import TestContentType
from zeit.cms.workflow.interfaces import IPublishInfo, IPublish
import gocept.testing.mock
import pytz
import threading
import time
import transaction
import zeit.cms.related.interfaces
import zeit.cms.testing
import zeit.workflow.publish
import zeit.workflow.testing
import zope.app.appsetup.product


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


class PublicationDependencies(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.WorkflowLayer

    def setUp(self):
        super(PublicationDependencies, self).setUp()
        self.patches = gocept.testing.mock.Patches()
        self.populate_repository_with_dummy_content()
        self.setup_dates_so_content_is_publishable()
        self.patches.add_dict(
            zope.app.appsetup.product.getProductConfiguration('zeit.workflow'),
            {'dependency-publish-limit': 2})

    def tearDown(self):
        self.patches.reset()
        super(PublicationDependencies, self).tearDown()

    def populate_repository_with_dummy_content(self):
        self.related = []
        for i in range(3):
            item = TestContentType()
            self.repository['t%s' % i] = item
            self.related.append(self.repository['t%s' % i])

    def setup_dates_so_content_is_publishable(self):
        DAY1 = datetime(2010, 1, 1, tzinfo=pytz.UTC)
        DAY2 = datetime(2010, 2, 1, tzinfo=pytz.UTC)
        DAY3 = datetime(2010, 3, 1, tzinfo=pytz.UTC)

        # XXX it would be nicer to patch this just for the items in question,
        # but we lack the mechanics to easily substitute adapter instances
        sem = self.patches.add('zeit.cms.content.interfaces.ISemanticChange')
        sem().last_semantic_change = DAY1
        sem().has_semantic_change = False
        for item in self.related:
            info = IPublishInfo(item)
            info.published = True
            info.date_last_published = DAY2
        dc = self.patches.add('zope.dublincore.interfaces.IDCTimes')
        dc().modified = DAY3

    def publish(self, content):
        IPublishInfo(content).urgent = True
        IPublish(content).publish()
        zeit.workflow.testing.run_publish()

    def test_should_not_publish_more_dependencies_than_the_limit_breadth(self):
        content = self.repository['testcontent']
        with checked_out(content) as co:
            IRelatedContent(co).related = tuple(self.related)

        BEFORE_PUBLISH = datetime.now(pytz.UTC)
        self.publish(content)

        self.assertEqual(
            2, len([x for x in self.related
                    if IPublishInfo(x).date_last_published > BEFORE_PUBLISH]))

    def test_should_not_publish_more_dependencies_than_the_limit_depth(self):
        content = [self.repository['testcontent']] + self.related
        for i in range(3):
            with checked_out(content[i]) as co:
                IRelatedContent(co).related = tuple([content[i+1]])

        BEFORE_PUBLISH = datetime.now(pytz.UTC)
        self.publish(content[0])

        self.assertEqual(
            2, len([x for x in self.related
                    if IPublishInfo(x).date_last_published > BEFORE_PUBLISH]))
