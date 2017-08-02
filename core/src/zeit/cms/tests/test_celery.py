from celery import shared_task
from mock import patch
import transaction
import zeit.cms.testing
import zeit.workflow.testing


@shared_task(queuename='publish_homepage')
def hp_task():
    """Task with queue homepage."""


@shared_task
def no_default_queue():
    """Task without a default queue."""


class RouteTaskTests(zeit.cms.testing.FunctionalTestCase):
    """Testing ..celery.route_task()."""

    layer = zeit.workflow.testing.ZEIT_CELERY_END_TO_END_LAYER

    def get_queue_name(self, task, **kw):
        result = task.apply_async(**kw)
        publish = 'celery.events.dispatcher.EventDispatcher.publish'
        with patch(publish) as publish:
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
