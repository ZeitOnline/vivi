import pendulum
import transaction

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.workflow.scheduled.cli import ScheduledOperationExecutor
from zeit.workflow.scheduled.interfaces import IScheduledOperations
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.workflow.testing


class ScheduledOperationsCLITest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.CELERY_LAYER

    def setUp(self):
        super().setUp()
        self.content = self.repository['testcontent']
        self.executor = ScheduledOperationExecutor()
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.urgent = True

    def test_execute_publishes_due_content(self):
        ops = IScheduledOperations(self.content)
        ops.add('publish', pendulum.now('UTC').add(seconds=-1))
        transaction.commit()

        self.executor.execute_all()

        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        self.assertTrue(info.published)

        # Operation should be deleted after execution
        self.assertEqual(0, len(ops.list()))

    def test_execute_skips_future_operations(self):
        ops = IScheduledOperations(self.content)
        ops.add('publish', pendulum.now('UTC').add(hours=1))
        transaction.commit()

        self.executor.execute_all()

        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        self.assertFalse(info.published)

        self.assertEqual(1, len(ops.list()))

    def test_execute_retracts_published_content(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.urgent = True
        publish = zeit.cms.workflow.interfaces.IPublish(self.content)
        publish.publish(background=False)
        self.assertTrue(info.published)

        ops = IScheduledOperations(self.content)
        ops.add('retract', pendulum.now('UTC').add(seconds=-1))
        transaction.commit()

        self.executor.execute_all()

        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        self.assertFalse(info.published)

        self.assertEqual(0, len(ops.list()))

    def test_execute_skips_retract_if_already_retracted(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        self.assertFalse(info.published)

        ops = IScheduledOperations(self.content)
        ops.add('retract', pendulum.now('UTC').add(seconds=-1))
        transaction.commit()

        self.executor.execute_all()

        self.assertEqual(0, len(ops.list()))

    def test_execute_applies_property_changes_before_publish(self):
        ops = IScheduledOperations(self.content)
        ops.add(
            'publish',
            pendulum.now('UTC').add(seconds=-1),
            property_changes={'access': 'abo'},
        )
        transaction.commit()

        self.executor.execute_all()

        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        self.assertTrue(info.published)

        self.assertEqual(0, len(ops.list()))

    def test_execute_processes_multiple_operations_in_order(self):
        self.repository['content2'] = ExampleContentType()
        content1 = self.repository['testcontent']
        content2 = self.repository['content2']
        transaction.commit()

        for content in [content1, content2]:
            info = zeit.cms.workflow.interfaces.IPublishInfo(content)
            info.urgent = True

        ops1 = IScheduledOperations(content1)
        ops2 = IScheduledOperations(content2)

        time1 = pendulum.now('UTC').add(seconds=-10)
        time2 = pendulum.now('UTC').add(seconds=-5)

        ops1.add('publish', time1)
        ops2.add('publish', time2)
        transaction.commit()

        self.executor.execute_all()

        info1 = zeit.cms.workflow.interfaces.IPublishInfo(content1)
        info2 = zeit.cms.workflow.interfaces.IPublishInfo(content2)
        self.assertTrue(info1.published)
        self.assertTrue(info2.published)

        self.assertEqual(0, len(ops1.list()))
        self.assertEqual(0, len(ops2.list()))

    def test_execute_deletes_operation_on_failure(self):
        ops = IScheduledOperations(self.content)

        ops.add(
            'publish',
            pendulum.now('UTC').add(seconds=-1),
            property_changes={'nonexistent_property': 'value'},
        )
        transaction.commit()

        self.executor.execute_all()
        self.assertEqual(0, len(ops.list()))

    def test_execute_handles_missing_content(self):
        ops = IScheduledOperations(self.content)
        _ = ops.add('publish', pendulum.now('UTC').add(seconds=-1))
        transaction.commit()

        del self.repository['testcontent']
        transaction.commit()

        self.executor.execute_all()
        self.assertEqual(0, len(ops.list()))

    def test_execute_with_empty_property_changes(self):
        ops = IScheduledOperations(self.content)
        ops.add('publish', pendulum.now('UTC').add(seconds=-1), property_changes={})
        transaction.commit()

        self.executor.execute_all()

        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        self.assertTrue(info.published)

    def test_execute_multiple_property_changes(self):
        ops = IScheduledOperations(self.content)
        ops.add(
            'publish',
            pendulum.now('UTC').add(seconds=-1),
            property_changes={'access': 'abo', 'product': 'ZEI'},
        )
        transaction.commit()

        self.executor.execute_all()

        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        self.assertTrue(info.published)

        self.assertEqual(0, len(ops.list()))
