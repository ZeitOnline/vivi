from ..timebased import TimeBasedWorkflow
from datetime import datetime, timedelta
from six import StringIO
from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import PRIORITY_TIMEBASED
import celery.result
import celery_longterm_scheduler
import logging
import pytz
import transaction
import zeit.cms.testing
import zeit.workflow.testing
import zope.component
import zope.i18n


class TimeBasedWorkflowTest(zeit.workflow.testing.FunctionalTestCase):

    def test_add_job_calls_apply_async_on_commit_with_eta_for_future_execution(
            self):
        workflow = TimeBasedWorkflow(
            zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent'))
        asynch = 'z3c.celery.celery.TransactionAwareTask._eager_use_session_'
        with mock.patch(
                'celery_longterm_scheduler.Task.apply_async') as apply_async, \
                mock.patch(asynch, new=True):
            workflow.add_job(
                zeit.workflow.publish.PUBLISH_TASK,
                datetime.now(pytz.UTC) + timedelta(1))
            self.assertEqual(False, apply_async.called)
            transaction.commit()

            self.assertEqual(True, apply_async.called)
            self.assertIn('eta', apply_async.call_args[1])
            self.assertEqual(
                PRIORITY_TIMEBASED, apply_async.call_args[1]['queue'])

    def test_should_schedule_job_for_renamed_uniqueId(self):
        with mock.patch('zeit.cms.celery.Task.apply_async') as apply_async, \
                checked_out(self.repository['testcontent']) as co:
            rn = zeit.cms.repository.interfaces.IAutomaticallyRenameable(co)
            rn.renameable = True
            rn.rename_to = 'changed'
            workflow = zeit.cms.workflow.interfaces.IPublishInfo(co)
            workflow.release_period = (
                datetime.now(pytz.UTC) + timedelta(days=1), None)
            transaction.commit()
            self.assertEqual(
                'http://xml.zeit.de/changed',
                apply_async.call_args[0][0][0][0])


class PrintImportSchedulingTest(zeit.workflow.testing.FunctionalTestCase):

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

    layer = zeit.workflow.testing.CELERY_LAYER

    def setUp(self):
        super(TimeBasedCeleryEndToEndTest, self).setUp()
        self.unique_id = 'http://xml.zeit.de/online/2007/01/Somalia'
        self.content = ICMSContent(self.unique_id)
        self.workflow = zeit.workflow.interfaces.IContentWorkflow(self.content)
        self.workflow.urgent = True
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
        super(TimeBasedCeleryEndToEndTest, self).tearDown()

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

        self.assertEllipsis("""\
Running job {0.workflow.publish_job_id} for http://xml.zeit.de/online/2007/01/Somalia
Publishing http://xml.zeit.de/online/2007/01/Somalia
...
Done http://xml.zeit.de/online/2007/01/Somalia ...""".format(self),  # noqa
                            self.log.getvalue())

    def test_released_from__in_future_is_published_later(self):
        publish_on = datetime.now(pytz.UTC) + timedelta(seconds=1.2)

        self.workflow.release_period = (publish_on, None)
        transaction.commit()

        scheduler = celery_longterm_scheduler.get_scheduler(
            self.layer['celery_app'])
        scheduler.execute_pending(publish_on)
        transaction.commit()

        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        assert 'Published.' == result.get()
        self.assertEllipsis("""\
Start executing tasks...
Enqueuing...
Revoked...
End executing tasks...
Running job {0.workflow.publish_job_id} for http://xml.zeit.de/online/2007/01/Somalia
Publishing http://xml.zeit.de/online/2007/01/Somalia
...
Done http://xml.zeit.de/online/2007/01/Somalia ...""".format(self),  # noqa
                            self.log.getvalue())

    def test_released_from__revokes_job_on_change(self):
        publish_on = datetime.now(pytz.UTC) + timedelta(days=1)

        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        job_id = self.workflow.publish_job_id
        scheduler = celery_longterm_scheduler.get_scheduler(
            self.layer['celery_app'])
        assert scheduler.backend.get(job_id)

        # The current job gets revoked on change of released_from:
        publish_on += timedelta(seconds=1)
        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        with self.assertRaises(KeyError):
            scheduler.backend.get(job_id)

        # The newly created job is pending its execution:
        new_job = self.workflow.publish_job_id
        assert scheduler.backend.get(new_job)

    def test_released_from__revokes_job_on_change_while_checked_out(self):
        publish_on = datetime.now(pytz.UTC) + timedelta(days=1)

        with checked_out(self.content) as co:
            workflow = zeit.cms.workflow.interfaces.IPublishInfo(co)
            workflow.release_period = (publish_on, None)
        transaction.commit()
        job_id = self.workflow.publish_job_id
        scheduler = celery_longterm_scheduler.get_scheduler(
            self.layer['celery_app'])
        assert scheduler.backend.get(job_id)

        # The current job gets revoked on change of released_from:
        publish_on += timedelta(seconds=1)
        with checked_out(self.content) as co:
            workflow = zeit.cms.workflow.interfaces.IPublishInfo(co)
            workflow.release_period = (publish_on, None)
        transaction.commit()
        with self.assertRaises(KeyError):
            scheduler.backend.get(job_id)

        # The newly created job is pending its execution:
        new_job = self.workflow.publish_job_id
        assert scheduler.backend.get(new_job)

    def test_released_to__in_past_retracts_instantly(self):
        zeit.cms.workflow.interfaces.IPublish(
            self.content).publish(background=False)
        transaction.commit()

        retract_on = datetime.now(pytz.UTC) + timedelta(seconds=-1)
        self.workflow.release_period = (None, retract_on)
        transaction.commit()

        result = celery.result.AsyncResult(self.workflow.retract_job_id)
        # Make sure the task is completed before asserting its output:
        assert 'Retracted.' == result.get()

        self.assertEllipsis("""...
Running job {0.workflow.retract_job_id} for http://xml.zeit.de/online/2007/01/Somalia
Retracting http://xml.zeit.de/online/2007/01/Somalia
...
Done http://xml.zeit.de/online/2007/01/Somalia ...""".format(self),  # noqa
                            self.log.getvalue())

    def test_released_to__in_future_is_retracted_later(self):
        zeit.cms.workflow.interfaces.IPublish(
            self.content).publish(background=False)
        transaction.commit()

        retract_on = datetime.now(pytz.UTC) + timedelta(seconds=1.5)
        self.workflow.release_period = (None, retract_on)
        transaction.commit()
        cancel_retract_job_id = self.workflow.retract_job_id
        scheduler = celery_longterm_scheduler.get_scheduler(
            self.layer['celery_app'])
        assert scheduler.backend.get(cancel_retract_job_id)

        # The current job gets revoked on change of released_to:
        new_retract_on = retract_on + timedelta(seconds=1)
        self.workflow.release_period = (None, new_retract_on)
        transaction.commit()
        with self.assertRaises(KeyError):
            scheduler.backend.get(cancel_retract_job_id)

        # The newly created job is pending its execution:
        new_job = self.workflow.retract_job_id
        assert scheduler.backend.get(new_job)

        # The actions are logged:
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log_entries = [zope.i18n.translate(e.message)
                       for e in log.get_log(self.content)]

        def berlin(dt):
            return TimeBasedWorkflow.format_datetime(dt)

        self.assertEqual([
            u'Urgent: yes',
            u'Published',
            u'To retract on {} (job #{})'.format(
                berlin(retract_on), cancel_retract_job_id),
            u'Scheduled retract cancelled (job #{}).'.format(
                cancel_retract_job_id),
            u'To retract on {} (job #{})'.format(
                berlin(new_retract_on), self.workflow.retract_job_id),
        ], log_entries)

    def test_removing_release_period_should_remove_jobid(self):
        self.workflow.release_period = (
            datetime.now(pytz.UTC) + timedelta(days=1), None)
        transaction.commit()
        self.assertNotEqual(None, self.workflow.publish_job_id)
        self.workflow.release_period = (None, None)
        transaction.commit()
        self.assertEqual(None, self.workflow.publish_job_id)
