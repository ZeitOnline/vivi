import pendulum
import pytest
import transaction

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.workflow.scheduled.interfaces import IScheduledOperations
import zeit.cms.testing
import zeit.workflow.testing


class ScheduledOperationsTest(zeit.workflow.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.content = self.repository['testcontent']

    def test_add_creates_operation(self):
        ops = IScheduledOperations(self.content)
        scheduled_time = pendulum.now('UTC').add(hours=1)

        op_id = ops.add('publish', scheduled_time)

        self.assertIsNotNone(op_id)
        operation_list = ops.list()
        self.assertEqual(1, len(operation_list))
        self.assertEqual(op_id, operation_list[0].id)
        self.assertEqual('publish', operation_list[0].operation)
        self.assertEqual(scheduled_time, operation_list[0].scheduled_on)

    def test_add_with_property_changes(self):
        ops = IScheduledOperations(self.content)
        scheduled_time = pendulum.now('UTC').add(hours=1)
        property_changes = {'access': 'abo', 'product': 'ZEI'}

        op_id = ops.add('publish', scheduled_time, property_changes=property_changes)

        operation = ops.get(op_id)
        self.assertEqual(property_changes, operation.property_changes)

    def test_remove_deletes_operation(self):
        ops = IScheduledOperations(self.content)
        scheduled_time = pendulum.now('UTC').add(hours=1)

        op_id = ops.add('publish', scheduled_time)
        ops.remove(op_id)

        self.assertEqual(0, len(ops.list()))

    def test_update_changes_scheduled_time(self):
        ops = IScheduledOperations(self.content)
        old_time = pendulum.now('UTC').add(hours=1)
        new_time = pendulum.now('UTC').add(hours=2)

        op_id = ops.add('publish', old_time)
        ops.update(op_id, scheduled_on=new_time)

        operation = ops.get(op_id)
        self.assertEqual(new_time, operation.scheduled_on)

    def test_update_changes_property_changes(self):
        ops = IScheduledOperations(self.content)
        scheduled_time = pendulum.now('UTC').add(hours=1)
        old_props = {'access': 'free'}
        new_props = {'access': 'abo', 'product': 'ZEI'}

        op_id = ops.add('publish', scheduled_time, property_changes=old_props)
        ops.update(op_id, property_changes=new_props)

        operation = ops.get(op_id)
        self.assertEqual(new_props, operation.property_changes)

    def test_list_returns_all_operations_sorted_by_time(self):
        ops = IScheduledOperations(self.content)
        time1 = pendulum.now('UTC').add(hours=3)
        time2 = pendulum.now('UTC').add(hours=1)
        time3 = pendulum.now('UTC').add(hours=2)

        ops.add('publish', time1)
        ops.add('retract', time2)
        ops.add('publish', time3)

        operation_list = ops.list()
        self.assertEqual(3, len(operation_list))
        # Should be sorted by scheduled_on
        self.assertEqual(time2, operation_list[0].scheduled_on)
        self.assertEqual(time3, operation_list[1].scheduled_on)
        self.assertEqual(time1, operation_list[2].scheduled_on)

    def test_list_filters_by_operation_type(self):
        ops = IScheduledOperations(self.content)
        time1 = pendulum.now('UTC').add(hours=1)
        time2 = pendulum.now('UTC').add(hours=2)

        ops.add('publish', time1)
        ops.add('retract', time2)

        publish_ops = ops.list(operation='publish')
        self.assertEqual(1, len(publish_ops))
        self.assertEqual('publish', publish_ops[0].operation)

        retract_ops = ops.list(operation='retract')
        self.assertEqual(1, len(retract_ops))
        self.assertEqual('retract', retract_ops[0].operation)

    def test_list_returns_empty_for_new_content(self):
        ops = IScheduledOperations(self.content)
        self.assertEqual([], ops.list())

    def test_get_returns_operation_by_id(self):
        ops = IScheduledOperations(self.content)
        scheduled_time = pendulum.now('UTC').add(hours=1)

        op_id = ops.add('publish', scheduled_time)

        operation = ops.get(op_id)
        self.assertEqual(op_id, operation.id)
        self.assertEqual('publish', operation.operation)
        self.assertEqual(scheduled_time, operation.scheduled_on)

    def test_multiple_operations_per_content(self):
        ops = IScheduledOperations(self.content)

        ops.add('publish', pendulum.now('UTC').add(days=1))
        ops.add('publish', pendulum.now('UTC').add(days=2), property_changes={'access': 'abo'})
        ops.add('retract', pendulum.now('UTC').add(days=3))

        operation_list = ops.list()
        self.assertEqual(3, len(operation_list))

    def test_operations_isolated_between_content_objects(self):
        content1 = self.repository['testcontent']
        content2 = self.repository['one']

        ops1 = IScheduledOperations(content1)
        ops2 = IScheduledOperations(content2)

        ops1.add('publish', pendulum.now('UTC').add(hours=1))
        ops2.add('publish', pendulum.now('UTC').add(hours=2))

        self.assertEqual(1, len(ops1.list()))
        self.assertEqual(1, len(ops2.list()))

    def test_created_by_stores_principal(self):
        ops = IScheduledOperations(self.content)
        op_id = ops.add('publish', pendulum.now('UTC').add(hours=1))

        operation = ops.get(op_id)
        self.assertEqual('zope.user', operation.created_by)

    def test_date_created_is_set_automatically(self):
        ops = IScheduledOperations(self.content)
        op_id = ops.add('publish', pendulum.now('UTC').add(hours=1))
        operation = ops.get(op_id)

        self.assertIsNotNone(operation.date_created)
        now = pendulum.now('UTC')
        diff = now - operation.date_created
        # Just check that date_created is recent (within last minute)
        self.assertLess(diff.total_seconds(), 60)

    def test_transaction_rollback_removes_operation(self):
        ops = IScheduledOperations(self.content)
        op_id = ops.add('publish', pendulum.now('UTC').add(hours=1))
        transaction.abort()

        with self.assertRaises(KeyError):
            ops.get(op_id)

    def test_empty_property_changes_dict_is_valid(self):
        ops = IScheduledOperations(self.content)
        scheduled_time = pendulum.now('UTC').add(hours=1)
        op_id = ops.add('publish', scheduled_time, property_changes={})
        operation = ops.get(op_id)
        self.assertEqual({}, operation.property_changes)

    @pytest.mark.xfail(reason='This needs to be resolved!')
    def test_non_persisted_content(self):
        testcontent = ExampleContentType()
        ops = IScheduledOperations(testcontent)
        scheduled_time = pendulum.now('UTC').add(hours=1)
        ops.add('publish', scheduled_time, property_changes={})
        self.assertEqual(1, len(ops.list()))
