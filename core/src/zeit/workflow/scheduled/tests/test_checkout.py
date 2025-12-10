import pendulum
import transaction

from zeit.workflow.scheduled.interfaces import IScheduledOperations
import zeit.cms.checkout.helper
import zeit.cms.checkout.interfaces
import zeit.workflow.testing


class CheckoutEventHandlerTest(zeit.workflow.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.content = self.repository['testcontent']

    def test_checkout_with_no_operations(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.content)
        co = manager.checkout()

        zodb_storage = IScheduledOperations(co)
        self.assertEqual(0, len(zodb_storage.list()))

    def test_checkout_copies_single_operation(self):
        ops = IScheduledOperations(self.content)
        scheduled_time = pendulum.now('UTC').add(hours=1)
        op_id = ops.add('publish', scheduled_time, property_changes={'access': 'abo'})
        transaction.commit()

        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            zodb_storage = IScheduledOperations(co)
            zodb_operations = zodb_storage.list()

            self.assertEqual(1, len(zodb_operations))

            zodb_op = zodb_storage.get(op_id)
            self.assertEqual('publish', zodb_op.operation)
            self.assertEqual(scheduled_time, zodb_op.scheduled_on)
            self.assertEqual({'access': 'abo'}, zodb_op.property_changes)

    def test_checkout_copies_multiple_operations(self):
        ops = IScheduledOperations(self.content)
        op1_id = ops.add('publish', pendulum.now('UTC').add(hours=1))
        op2_id = ops.add('retract', pendulum.now('UTC').add(hours=2))
        op3_id = ops.add('publish', pendulum.now('UTC').add(hours=3))
        transaction.commit()

        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            zodb_storage = IScheduledOperations(co)
            zodb_operations = zodb_storage.list()

            self.assertEqual(3, len(zodb_operations))
            self.assertIsNotNone(zodb_storage.get(op1_id))
            self.assertIsNotNone(zodb_storage.get(op2_id))
            self.assertIsNotNone(zodb_storage.get(op3_id))

    def test_checkout_preserves_operation_metadata(self):
        ops = IScheduledOperations(self.content)
        scheduled_time = pendulum.parse('2025-12-01 10:00:00')
        property_changes = {'access': 'abo', 'product': 'ZEI'}
        op_id = ops.add('publish', scheduled_time, property_changes)
        transaction.commit()

        sql_storage = IScheduledOperations(self.content)
        sql_op = sql_storage.get(op_id)
        sql_created_by = sql_op.created_by
        sql_date_created = sql_op.date_created

        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            zodb_storage = IScheduledOperations(co)
            zodb_op = zodb_storage.get(op_id)

            self.assertEqual(op_id, zodb_op.id)
            self.assertEqual('publish', zodb_op.operation)
            self.assertEqual(scheduled_time, zodb_op.scheduled_on)
            self.assertEqual(property_changes, zodb_op.property_changes)
            self.assertEqual(sql_created_by, zodb_op.created_by)
            self.assertEqual(sql_date_created, zodb_op.date_created)


class CheckinEventHandlerTest(zeit.workflow.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.content = self.repository['testcontent']

    def test_checkin_with_no_changes(self):
        ops = IScheduledOperations(self.content)
        op_id = ops.add('publish', pendulum.now('UTC').add(hours=1))
        transaction.commit()

        with zeit.cms.checkout.helper.checked_out(self.content):
            pass

        sql_storage = IScheduledOperations(self.content)
        sql_op = sql_storage.get(op_id)
        self.assertIsNotNone(sql_op)
        self.assertEqual('publish', sql_op.operation)

    def test_checkin_adds_new_operation(self):
        new_op_id = None

        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            ops = IScheduledOperations(co)
            new_op_id = ops.add('publish', pendulum.now('UTC').add(hours=1))

        sql_storage = IScheduledOperations(self.content)
        sql_op = sql_storage.get(new_op_id)
        self.assertIsNotNone(sql_op)
        self.assertEqual('publish', sql_op.operation)

    def test_checkin_removes_deleted_operation(self):
        ops = IScheduledOperations(self.content)
        op_id = ops.add('publish', pendulum.now('UTC').add(hours=1))
        transaction.commit()

        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            co_ops = IScheduledOperations(co)
            co_ops.remove(op_id)

        sql_storage = IScheduledOperations(self.content)
        with self.assertRaises(KeyError):
            sql_storage.get(op_id)

    def test_checkin_updates_modified_operation(self):
        ops = IScheduledOperations(self.content)
        original_time = pendulum.now('UTC').add(hours=1)
        op_id = ops.add('publish', original_time)
        transaction.commit()

        new_time = pendulum.now('UTC').add(hours=5)
        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            co_ops = IScheduledOperations(co)
            co_ops.update(op_id, scheduled_on=new_time)

        sql_storage = IScheduledOperations(self.content)
        sql_op = sql_storage.get(op_id)
        self.assertIsNotNone(sql_op)
        self.assertEqual(new_time, sql_op.scheduled_on)

    def test_checkin_replaces_all_operations(self):
        ops = IScheduledOperations(self.content)
        old_op1_id = ops.add('publish', pendulum.now('UTC').add(hours=1))
        old_op2_id = ops.add('retract', pendulum.now('UTC').add(hours=2))
        transaction.commit()

        new_op1_id = None
        new_op2_id = None
        new_op3_id = None

        with zeit.cms.checkout.helper.checked_out(self.content) as co:
            co_ops = IScheduledOperations(co)

            co_ops.remove(old_op1_id)
            co_ops.remove(old_op2_id)

            new_op1_id = co_ops.add('publish', pendulum.now('UTC').add(hours=10))
            new_op2_id = co_ops.add('retract', pendulum.now('UTC').add(hours=11))
            new_op3_id = co_ops.add('publish', pendulum.now('UTC').add(hours=12))

        sql_storage = IScheduledOperations(self.content)

        with self.assertRaises(KeyError):
            sql_storage.get(old_op1_id)
        with self.assertRaises(KeyError):
            sql_storage.get(old_op2_id)

        self.assertIsNotNone(sql_storage.get(new_op1_id))
        self.assertIsNotNone(sql_storage.get(new_op2_id))
        self.assertIsNotNone(sql_storage.get(new_op3_id))


class DeleteEventHandlerTest(zeit.workflow.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.content = self.repository['testcontent']

    def test_delete_with_no_operations(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.content)
        co = manager.checkout()

        del_manager = zeit.cms.checkout.interfaces.ICheckinManager(co)
        del_manager.delete()

        transaction.commit()

    def test_delete_discards_zodb_operations(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.content)
        co = manager.checkout()

        ops = IScheduledOperations(co)
        op_id = ops.add('publish', pendulum.now('UTC').add(hours=1))
        transaction.commit()

        zodb_storage = IScheduledOperations(co)
        self.assertIsNotNone(zodb_storage.get(op_id))

        del_manager = zeit.cms.checkout.interfaces.ICheckinManager(co)
        del_manager.delete()
        transaction.commit()

        sql_storage = IScheduledOperations(self.content)
        with self.assertRaises(KeyError):
            sql_storage.get(op_id)

    def test_delete_preserves_sql_operations(self):
        ops = IScheduledOperations(self.content)
        original_op_id = ops.add('publish', pendulum.now('UTC').add(hours=1))
        transaction.commit()

        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.content)
        co = manager.checkout()

        co_ops = IScheduledOperations(co)
        new_op_id = co_ops.add('retract', pendulum.now('UTC').add(hours=2))
        transaction.commit()

        del_manager = zeit.cms.checkout.interfaces.ICheckinManager(co)
        del_manager.delete()
        transaction.commit()

        sql_storage = IScheduledOperations(self.content)
        sql_op = sql_storage.get(original_op_id)
        self.assertIsNotNone(sql_op)
        self.assertEqual('publish', sql_op.operation)

        with self.assertRaises(KeyError):
            sql_storage.get(new_op_id)
