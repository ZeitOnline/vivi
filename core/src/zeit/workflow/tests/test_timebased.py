from io import StringIO
import logging

import pendulum
import transaction

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.workflow.interfaces import ITimeBasedPublishing
from zeit.workflow.scheduled.interfaces import IScheduledOperations
import zeit.cms.testing
import zeit.cms.workflow
import zeit.workflow.testing

from ..cli import _publish_scheduled_content, _retract_scheduled_content


class TimeBasedEndToEndTest(zeit.workflow.testing.FunctionalTestCase):
    # Cannot use savepoint isolation, since `now()` returns the transaction
    # start time, which does not change in nested transactions.
    layer = zeit.workflow.testing.CELERY_LAYER

    def setUp(self):
        super().setUp()

        self.content = self.repository['testcontent']
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.urgent = True

        self.log = StringIO()
        self.handler = logging.StreamHandler(self.log)
        logging.root.addHandler(self.handler)
        self.loggers = [None, 'zeit']
        self.oldlevels = {}
        for name in self.loggers:
            log = logging.getLogger(name)
            self.oldlevels[name] = log.level
            log.setLevel(logging.INFO)

    def tearDown(self):
        logging.root.removeHandler(self.handler)
        for name in self.loggers:
            logging.getLogger(name).setLevel(self.oldlevels[name])
        super().tearDown()

    def test_scheduled_publish(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_from = pendulum.now('UTC').add(seconds=100)
        _publish_scheduled_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertNotEllipsis(f'...Publishing {self.content.uniqueId}...', self.log.getvalue())

        info.released_from = pendulum.now('UTC').add(seconds=-1)
        _publish_scheduled_content()
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Publishing {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_republish(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_to = pendulum.now('UTC').add(hours=1)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.published = True
        info.date_last_published = pendulum.now('UTC').add(hours=-1)
        info.released_from = pendulum.now('UTC').add(seconds=-1)
        _publish_scheduled_content()
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Publishing {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_retract(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_to = pendulum.now('UTC').add(hours=1)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.published = True
        info.date_last_published = pendulum.now('UTC').add(hours=-1)
        _retract_scheduled_content()
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertNotEllipsis(f'...Retracting {self.content.uniqueId}...', self.log.getvalue())

        info.released_to = pendulum.now('UTC').add(seconds=-1)
        _retract_scheduled_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Retracting {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_retract_skip_retract_if_locking_error(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_to = pendulum.now('UTC').add(seconds=-1)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.published = True
        info.date_last_published = pendulum.now('UTC').add(hours=-1)
        transaction.commit()

        until = pendulum.now('UTC').add(minutes=1)
        self.repository.connector.lock(self.content.uniqueId, 'someone', until)
        _retract_scheduled_content()
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Skip ... {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_publish_skip_if_publish_error(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.urgent = False
        info.released_from = pendulum.now('UTC').add(seconds=-1)
        _publish_scheduled_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Skip ... {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_publish_respect_margin_to_retract(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_from = pendulum.now('UTC').add(minutes=-2)
        info.released_to = pendulum.now('UTC').add(minutes=5)
        _publish_scheduled_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertNotEllipsis(f'...Publishing {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_publish_consider_manual_retract(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_from = pendulum.now('UTC').add(minutes=-2)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        # the last retract is more recent than the scheduled publish date
        # therefore we do not publish!
        info.date_last_retracted = pendulum.now('UTC').add(minutes=2)
        _publish_scheduled_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertNotEllipsis(f'...Publishing {self.content.uniqueId}...', self.log.getvalue())


class TimeBasedScheduledOperationsTest(zeit.workflow.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.content = self.repository['testcontent']

    def test_setting_released_from_creates_publish_operation(self):
        info = ITimeBasedPublishing(self.content)
        future_time = pendulum.now('UTC').add(hours=2)
        info.release_period = (future_time, None)

        ops = IScheduledOperations(self.content)
        publish_ops = [op for op in ops.list(operation='publish') if not op.property_changes]

        self.assertEqual(1, len(publish_ops))
        self.assertEqual(future_time, publish_ops[0].scheduled_on)

    def test_setting_released_to_creates_retract_operation(self):
        info = ITimeBasedPublishing(self.content)
        future_time = pendulum.now('UTC').add(hours=3)
        info.release_period = (None, future_time)

        ops = IScheduledOperations(self.content)
        retract_ops = [op for op in ops.list(operation='retract') if not op.property_changes]

        self.assertEqual(1, len(retract_ops))
        self.assertEqual(future_time, retract_ops[0].scheduled_on)

    def test_updating_released_from_updates_existing_operation(self):
        info = ITimeBasedPublishing(self.content)
        time1 = pendulum.now('UTC').add(hours=1)
        time2 = pendulum.now('UTC').add(hours=2)

        info.release_period = (time1, None)
        ops = IScheduledOperations(self.content)
        op_id_before = ops.list(operation='publish')[0].id

        info.release_period = (time2, None)
        ops_after = [op for op in ops.list(operation='publish') if not op.property_changes]

        self.assertEqual(1, len(ops_after))
        self.assertEqual(op_id_before, ops_after[0].id)
        self.assertEqual(time2, ops_after[0].scheduled_on)

    def test_clearing_released_from_removes_operation(self):
        info = ITimeBasedPublishing(self.content)
        info.release_period = (pendulum.now('UTC').add(hours=1), None)

        ops = IScheduledOperations(self.content)
        self.assertEqual(1, len(ops.list(operation='publish')))

        info.release_period = (None, None)
        self.assertEqual(
            0, len([op for op in ops.list(operation='publish') if not op.property_changes])
        )

    def test_past_timestamp_removes_operation(self):
        info = ITimeBasedPublishing(self.content)
        info.release_period = (pendulum.now('UTC').add(hours=1), None)

        ops = IScheduledOperations(self.content)
        self.assertEqual(1, len(ops.list(operation='publish')))

        info.release_period = (pendulum.now('UTC').subtract(hours=1), None)
        self.assertEqual(
            0, len([op for op in ops.list(operation='publish') if not op.property_changes])
        )

    def test_does_not_remove_operations_with_property_changes(self):
        ops = IScheduledOperations(self.content)
        future_time = pendulum.now('UTC').add(hours=2)
        op_id = ops.add('publish', future_time, property_changes={'access': 'abo'})

        info = ITimeBasedPublishing(self.content)
        info.release_period = (None, None)

        all_ops = ops.list(operation='publish')
        self.assertEqual(1, len(all_ops))
        self.assertEqual(op_id, all_ops[0].id)

    def test_setting_release_period_tuple(self):
        info = ITimeBasedPublishing(self.content)
        from_time = pendulum.now('UTC').add(hours=1)
        to_time = pendulum.now('UTC').add(hours=3)

        info.release_period = (from_time, to_time)

        ops = IScheduledOperations(self.content)
        publish_ops = [op for op in ops.list(operation='publish') if not op.property_changes]
        retract_ops = [op for op in ops.list(operation='retract') if not op.property_changes]

        self.assertEqual(1, len(publish_ops))
        self.assertEqual(1, len(retract_ops))
        self.assertEqual(from_time, publish_ops[0].scheduled_on)
        self.assertEqual(to_time, retract_ops[0].scheduled_on)

    def test_feature_toggle_disabled_skips_sync(self):
        FEATURE_TOGGLES.unset('use_scheduled_operations')

        info = ITimeBasedPublishing(self.content)
        info.release_period = (pendulum.now('UTC').add(hours=2), None)

        ops = IScheduledOperations(self.content)
        self.assertEqual(0, len(ops.list(operation='publish')))
