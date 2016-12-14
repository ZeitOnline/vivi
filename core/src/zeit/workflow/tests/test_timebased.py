import zope.i18n
import zope.component
from ..timebased import TimeBasedWorkflow
from zeit.cms.interfaces import ICMSContent
import celery.result
import datetime
import mock
import pytz
import time
import transaction
import zeit.cms.testing
import zeit.content.article.cds
import zeit.content.article.testing
import zeit.workflow.testing


class TimeBasedWorkflowTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.ZCML_LAYER

    def test_add_job_calls_async_celery_task_with_delay_for_future_execution(
            self):
        workflow = TimeBasedWorkflow(
            zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent'))
        run_instantly = 'z3c.celery.celery.TransactionAwareTask.run_instantly'
        with zeit.cms.testing.site(self.getRootFolder()), \
                mock.patch('celery.Task.apply_async') as apply_async, \
                mock.patch(run_instantly, return_value=False):
            workflow.add_job(
                zeit.workflow.publish.PUBLISH_TASK,
                datetime.datetime.now(pytz.UTC) + datetime.timedelta(1))

            transaction.commit()  # needed as we are async here

            assert apply_async.called
            self.assertIn('countdown', apply_async.call_args[1])


class TimeBasedWorkflowEndToEndTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.ZEIT_CELERY_END_TO_END_LAYER

    def setUp(self):
        super(TimeBasedWorkflowEndToEndTest, self).setUp()
        self.unique_id = 'http://xml.zeit.de/online/2007/01/Somalia-urgent'
        self.content = ICMSContent(self.unique_id)
        self.workflow = zeit.workflow.interfaces.IContentWorkflow(self.content)

    def test_time_based_workflow_basic_assumptions(self):
        assert not self.workflow.published
        assert (None, None) == self.workflow.release_period
        assert 'can-publish-success' == self.workflow.can_publish()

    def test_released_from__in_past_is_published_instantly(self):
        publish_on = (
            datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=-1))

        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        # Make sure the task is completed before asserting its output:
        assert 'Published.' == result.get()

        with open(self.layer['logfile_name']) as logfile:
            self.assertEllipsis('''\
Running job {0.workflow.publish_job_id}
Publishing http://xml.zeit.de/online/2007/01/Somalia-urgent
Done http://xml.zeit.de/online/2007/01/Somalia-urgent (...s)'''.format(self),
                                logfile.read())

    def test_released_from__in_future_is_published_later(self):
        publish_on = (
            datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=1.2))

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
Running job {0.workflow.publish_job_id}
Publishing http://xml.zeit.de/online/2007/01/Somalia-urgent
Done http://xml.zeit.de/online/2007/01/Somalia-urgent (...s)
Task zeit.workflow.publish.PUBLISH_TASK[...] succeeded in ...""".format(self),
                                logfile.read())

    def test_released_from__revokes_job_on_change(self):
        publish_on = (
            datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=1.2))

        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        assert u'PENDING' == result.state

        # The current job gets revoked on change of released_from:
        publish_on += datetime.timedelta(seconds=1)
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

    def test_released_to__in_past_retracts_instantly(self):
        publish_on = datetime.datetime(2000, 2, 3, tzinfo=pytz.UTC)
        retract_on = (
            datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=-1))
        self.workflow.release_period = (publish_on, retract_on)
        transaction.commit()

        result = celery.result.AsyncResult(self.workflow.retract_job_id)
        # Make sure the task is completed before asserting its output:
        assert 'Retracted.' == result.get()

        with open(self.layer['logfile_name']) as logfile:
            self.assertEllipsis('''...
Running job {0.workflow.retract_job_id}
Retracting http://xml.zeit.de/online/2007/01/Somalia-urgent
Done http://xml.zeit.de/online/2007/01/Somalia-urgent (...s)'''.format(self),
                                logfile.read())

    def test_released_to__in_future_is_retracted_later(self):
        publish_on = datetime.datetime(2000, 2, 3, tzinfo=pytz.UTC)
        retract_on = (
            datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=1.5))

        self.workflow.release_period = (publish_on, retract_on)
        transaction.commit()
        cancel_retract_job_id = self.workflow.retract_job_id
        result = celery.result.AsyncResult(cancel_retract_job_id)
        assert u'PENDING' == result.state

        # The current job gets revoked on change of released_to:
        new_retract_on = retract_on + datetime.timedelta(seconds=1)
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
            u'To be published on 2000 2 3  01:00:00  (job #{})'.format(
                self.workflow.publish_job_id),
            u'To be retracted on {} (job #{})'.format(
                berlin(retract_on), cancel_retract_job_id),
            u'Scheduled retracting cancelled (job #{}).'.format(
                cancel_retract_job_id),
            u'To be retracted on {} (job #{})'.format(
                berlin(new_retract_on), self.workflow.retract_job_id),
        ] == log_entries
