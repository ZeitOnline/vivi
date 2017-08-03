from ..timebased import TimeBasedWorkflow
from datetime import datetime, timedelta
from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import PRIORITY_TIMEBASED
import celery.result
import mock
import pytz
import time
import transaction
import zeit.cms.testing
import zeit.workflow.testing
import zope.component
import zope.i18n


class TimeBasedWorkflowTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.LAYER

    def test_add_job_calls_async_celery_task_with_delay_for_future_execution(
            self):
        workflow = TimeBasedWorkflow(
            zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent'))
        async = 'z3c.celery.celery.TransactionAwareTask._eager_use_session_'
        with mock.patch('celery.Task.apply_async') as apply_async, \
                mock.patch(async, new=True):
            workflow.add_job(
                zeit.workflow.publish.PUBLISH_TASK,
                datetime.now(pytz.UTC) + timedelta(1))

            transaction.commit()  # needed as we are async here

            self.assertEqual(True, apply_async.called)
            self.assertIn('countdown', apply_async.call_args[1])
            self.assertEqual(
                PRIORITY_TIMEBASED, apply_async.call_args[1]['queuename'])

    def test_should_schedule_job_for_renamed_uniqueId(self):
        async = 'z3c.celery.celery.TransactionAwareTask._eager_use_session_'
        with mock.patch('celery.Task.apply_async') as apply_async, \
                mock.patch(async, new=True), \
                checked_out(self.repository['testcontent']) as co:
            rn = zeit.cms.repository.interfaces.IAutomaticallyRenameable(co)
            rn.renameable = True
            rn.rename_to = 'changed'
            workflow = zeit.cms.workflow.interfaces.IPublishInfo(co)
            workflow.release_period = (
                datetime.now(pytz.UTC) + timedelta(days=1), None)
            transaction.commit()  # needed as we are async here
            self.assertEqual(
                'http://xml.zeit.de/changed',
                apply_async.call_args[0][0][0][0])


class PrintImportSchedulingTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.LAYER

    def test_should_schedule_job_when_no_jobid_present(self):
        content = self.repository['testcontent']
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        workflow.released_to = datetime.now(pytz.UTC) + timedelta(days=1)
        self.assertEqual(None, workflow.retract_job_id)
        zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(
            content, content))
        self.assertNotEqual(None, workflow.retract_job_id)

    def test_jobid_present_should_do_nothing(self):
        content = self.repository['testcontent']
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        workflow.release_period = (
            None, datetime.now(pytz.UTC) + timedelta(days=1))
        self.assertNotEqual(None, workflow.retract_job_id)
        with mock.patch('zeit.workflow.timebased.'
                        'TimeBasedWorkflow.setup_job') as setup_job:
            zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(
                content, content))
            self.assertFalse(setup_job.called)

    def test_no_retract_time_present_should_do_nothing(self):
        content = self.repository['testcontent']
        with mock.patch('zeit.workflow.timebased.'
                        'TimeBasedWorkflow.setup_job') as setup_job:
            zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(
                content, content))
            self.assertFalse(setup_job.called)

    def test_retract_time_in_the_past_should_not_schedule_again(self):
        content = self.repository['testcontent']
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        workflow.release_period = (
            None, datetime.now(pytz.UTC) + timedelta(days=-1))
        with mock.patch('zeit.workflow.timebased.'
                        'TimeBasedWorkflow.setup_job') as setup_job:
            zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(
                content, content))
            self.assertFalse(setup_job.called)


class TimeBasedCeleryEndToEndTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.ZEIT_CELERY_END_TO_END_LAYER

    def setUp(self):
        super(TimeBasedCeleryEndToEndTest, self).setUp()
        self.unique_id = 'http://xml.zeit.de/online/2007/01/Somalia-urgent'
        self.content = ICMSContent(self.unique_id)
        self.workflow = zeit.workflow.interfaces.IContentWorkflow(self.content)

    def test_time_based_workflow_basic_assumptions(self):
        assert not self.workflow.published
        assert (None, None) == self.workflow.release_period
        assert 'can-publish-success' == self.workflow.can_publish()

    def test_released_from__in_past_is_published_instantly(self):
        publish_on = datetime.now(pytz.UTC) + timedelta(seconds=-1)

        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        # Make sure the task is completed before asserting its output:
        assert 'Published.' == result.get()

        with open(self.layer['logfile_name']) as logfile:
            self.assertEllipsis('''\
Running job {0.workflow.publish_job_id} for http://xml.zeit.de/online/2007/01/Somalia-urgent
Publishing http://xml.zeit.de/online/2007/01/Somalia-urgent
Done http://xml.zeit.de/online/2007/01/Somalia-urgent ...'''.format(self),  # noqa
                                logfile.read())

    def test_released_from__in_future_is_published_later(self):
        publish_on = datetime.now(pytz.UTC) + timedelta(seconds=1.2)

        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        assert u'PENDING' == result.state

        # Let's wait a second and process; still not published:
        time.sleep(1)
        assert u'PENDING' == result.state

        # Waiting another second will at least start to publish the object:
        time.sleep(1)
        assert result.state in (u'STARTED', u'SUCCESS')

        # Make sure the task is completed before asserting its output:
        assert 'Published.' == result.get()
        with open(self.layer['logfile_name']) as logfile:
            self.assertEllipsis("""\
Running job {0.workflow.publish_job_id} for http://xml.zeit.de/online/2007/01/Somalia-urgent
Publishing http://xml.zeit.de/online/2007/01/Somalia-urgent
Done http://xml.zeit.de/online/2007/01/Somalia-urgent (...s)
Task zeit.workflow.publish.PUBLISH_TASK[...] succeeded in ...""".format(self),  # noqa
                                logfile.read())

    def test_released_from__revokes_job_on_change(self):
        publish_on = datetime.now(pytz.UTC) + timedelta(seconds=1.2)

        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        assert u'PENDING' == result.state

        # The current job gets revoked on change of released_from:
        publish_on += timedelta(seconds=1)
        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        assert u'PENDING' == result.state
        with self.assertRaises(Exception) as err:
            # The state is only changed after the timeout is reached.
            result.wait()
        assert 'TaskRevokedError' == err.exception.__class__.__name__
        assert u'REVOKED' == result.state

        # The newly created job is pending its execution:
        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        assert u'PENDING' == result.state
        result.get()  # make sure we do not violate test isolation

    def test_released_from__revokes_job_on_change_while_checked_out(self):
        publish_on = datetime.now(pytz.UTC) + timedelta(seconds=1.2)

        with checked_out(self.content) as co:
            workflow = zeit.cms.workflow.interfaces.IPublishInfo(co)
            workflow.release_period = (publish_on, None)
        transaction.commit()
        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        assert u'PENDING' == result.state

        # The current job gets revoked on change of released_from:
        publish_on += timedelta(seconds=1)
        with checked_out(self.content) as co:
            workflow = zeit.cms.workflow.interfaces.IPublishInfo(co)
            workflow.release_period = (publish_on, None)
        transaction.commit()
        assert u'PENDING' == result.state
        with self.assertRaises(Exception) as err:
            # The state is only changed after the timeout is reached.
            result.wait()
        assert 'TaskRevokedError' == err.exception.__class__.__name__
        assert u'REVOKED' == result.state

        # The newly created job is pending its execution:
        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        assert u'PENDING' == result.state
        result.get()  # make sure we do not violate test isolation

    def test_released_to__in_past_retracts_instantly(self):
        publish_on = datetime(2000, 2, 3, tzinfo=pytz.UTC)
        retract_on = datetime.now(pytz.UTC) + timedelta(seconds=-1)
        self.workflow.release_period = (publish_on, retract_on)
        transaction.commit()

        result = celery.result.AsyncResult(self.workflow.retract_job_id)
        # Make sure the task is completed before asserting its output:
        assert 'Retracted.' == result.get()

        with open(self.layer['logfile_name']) as logfile:
            self.assertEllipsis("""...
Running job {0.workflow.retract_job_id} for http://xml.zeit.de/online/2007/01/Somalia-urgent
Retracting http://xml.zeit.de/online/2007/01/Somalia-urgent
Done http://xml.zeit.de/online/2007/01/Somalia-urgent ...""".format(self),  # noqa
                                logfile.read())

    def test_released_to__in_future_is_retracted_later(self):
        publish_on = datetime(2000, 2, 3, tzinfo=pytz.UTC)
        retract_on = datetime.now(pytz.UTC) + timedelta(seconds=1.5)

        self.workflow.release_period = (publish_on, retract_on)
        transaction.commit()
        cancel_retract_job_id = self.workflow.retract_job_id
        result = celery.result.AsyncResult(cancel_retract_job_id)
        assert u'PENDING' == result.state

        # The current job gets revoked on change of released_to:
        new_retract_on = retract_on + timedelta(seconds=1)
        self.workflow.release_period = (publish_on, new_retract_on)
        transaction.commit()
        assert u'PENDING' == result.state
        with self.assertRaises(Exception) as err:
            # The state is only changed after the timeout is reached.
            result.wait()
        assert 'TaskRevokedError' == err.exception.__class__.__name__
        assert u'REVOKED' == result.state

        # The newly created job is pending its execution:
        result = celery.result.AsyncResult(self.workflow.retract_job_id)
        assert u'PENDING' == result.state
        result.get()  # make sure we do not violate test isolation

        # The actions are logged:
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log_entries = [zope.i18n.translate(e.message)
                       for e in log.get_log(self.content)]

        def berlin(dt):
            return TimeBasedWorkflow.format_datetime(dt)

        assert [
            u'To publish on 2000 2 3  01:00:00  (job #{})'.format(
                self.workflow.publish_job_id),
            u'To retract on {} (job #{})'.format(
                berlin(retract_on), cancel_retract_job_id),
            u'Scheduled retract cancelled (job #{}).'.format(
                cancel_retract_job_id),
            u'To retract on {} (job #{})'.format(
                berlin(new_retract_on), self.workflow.retract_job_id),
        ] == log_entries

    def test_removing_release_period_should_remove_jobid(self):
        self.workflow.release_period = (
            datetime.now(pytz.UTC) + timedelta(days=1), None)
        self.assertNotEqual(None, self.workflow.publish_job_id)
        self.workflow.release_period = (None, None)
        self.assertEqual(None, self.workflow.publish_job_id)
