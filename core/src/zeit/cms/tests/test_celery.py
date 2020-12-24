from unittest import mock
import transaction
import zeit.cms.celery
import zeit.workflow.testing


@zeit.cms.celery.task(queuename='publish_homepage')
def hp_task():
    """Task with queue homepage."""


@zeit.cms.celery.task
def no_default_queue():
    """Task without a default queue."""


class RouteTaskTests(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.CELERY_LAYER

    def get_queue_name(self, task, **kw):
        result = task.apply_async(**kw)
        publish = 'celery.events.dispatcher.EventDispatcher.publish'
        with mock.patch(publish) as publish:
            transaction.commit()
        result.get()
        assert 'task-sent' == publish.call_args[0][0]
        return publish.call_args[0][1]['queue']

    def test_route_task__returns_default_if_none_given(self):
        assert 'default' == self.get_queue_name(no_default_queue)

    def test_route_task__returns_queue_depending_on_name_set_on_task(self):
        assert 'publish_homepage' == self.get_queue_name(hp_task)

    def test_route_task__returns_queue_depending_on_name_set_on_call(self):
        assert 'publish_highprio' == self.get_queue_name(
            no_default_queue, queuename='publish_highprio')

    def test_route_task__priorizes_call_over_task_setting(self):
        assert 'publish_lowprio' == self.get_queue_name(
            hp_task, queuename='publish_lowprio')
