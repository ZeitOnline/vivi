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
        with self.assertLogs() as captured:
            self.run_task()
        assert 'ERROR' in captured[1][0]
        assert 'task_that_fails' in captured[1][0]
        assert 'RuntimeError' in captured[1][0]
