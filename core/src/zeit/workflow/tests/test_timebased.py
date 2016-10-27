import datetime
import mock
import pytz
import transaction
import zeit.content.article.cds
import zeit.content.article.testing


class TimeBasedWorkflowTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.cms.testing.ZCML_LAYER

    def test_add_job_calls_async_celery_task_with_delay_for_future_execution(
            self):
        workflow = zeit.workflow.timebased.TimeBasedWorkflow(
            zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent'))
        with zeit.cms.testing.site(self.getRootFolder()):
            with mock.patch(
                    'celery.Task.apply_async') as apply_async:
                workflow.add_job(
                    zeit.workflow.publish.PUBLISH_TASK,
                    datetime.datetime.now(pytz.UTC) + datetime.timedelta(1))

                transaction.commit()

                self.assertIn('countdown', apply_async.call_args[1])
