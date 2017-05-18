from datetime import datetime, timedelta
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
