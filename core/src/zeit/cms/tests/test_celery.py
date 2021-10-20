import transaction
import zeit.cms.celery
import zeit.workflow.testing


@zeit.cms.celery.task
def task_that_fails():
    raise RuntimeError()


class CelerySignalTests(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.CELERY_LAYER

    def run_task(self):
        result = task_that_fails.delay()
        transaction.commit()
        with self.assertRaises(RuntimeError):
            result.get()

    def test_failing_tasks_will_be_logged(self):
        with self.assertLogs() as capture:
            self.run_task()
        log = '\n'.join(capture.output)
        self.assertEllipsis(
            '...ERROR:...task_that_fails...RuntimeError...', log)
