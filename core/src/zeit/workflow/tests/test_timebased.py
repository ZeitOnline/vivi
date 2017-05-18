from datetime import datetime, timedelta
from zeit.cms.checkout.helper import checked_out
import lovely.remotetask.interfaces
import pytz
import zeit.cms.testing
import zeit.workflow.testing
import zope.component


class TimeBasedWorkflowTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.LAYER

    def test_removing_release_period_should_remove_jobid(self):
        content = self.repository['testcontent']
        workflow = zeit.workflow.interfaces.IContentWorkflow(content)
        workflow.release_period = (
            datetime.now(pytz.UTC) + timedelta(days=1), None)
        self.assertNotEqual(None, workflow.publish_job_id)
        # Put job into "delayed" state, otherwise it won't cancel.
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')
        tasks.process()
        workflow.release_period = (None, None)
        self.assertEqual(None, workflow.publish_job_id)

    def test_should_cancel_job_when_changed_during_checkout(self):
        content = self.repository['testcontent']
        workflow = zeit.workflow.interfaces.IContentWorkflow(content)
        with checked_out(content) as co:
            workflow = zeit.workflow.interfaces.IContentWorkflow(co)
            workflow.release_period = (
                datetime.now(pytz.UTC) + timedelta(days=1), None)
        # Put job into "delayed" state, otherwise it won't cancel.
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')
        tasks.process()
        job1 = workflow.publish_job_id
        self.assertNotEqual(None, job1)
        self.assertEqual('delayed', tasks.getStatus(job1))

        with checked_out(content) as co:
            workflow = zeit.workflow.interfaces.IContentWorkflow(co)
            workflow.release_period = (
                datetime.now(pytz.UTC) + timedelta(days=2), None)
        tasks.process()
        job2 = workflow.publish_job_id
        self.assertNotEqual(None, job2)
        self.assertNotEqual(job1, job2)
        self.assertEqual('cancelled', tasks.getStatus(job1))
        self.assertEqual('delayed', tasks.getStatus(job2))
