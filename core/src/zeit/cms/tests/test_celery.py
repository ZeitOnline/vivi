from celery import shared_task
from mock import patch
import transaction
import zeit.cms.testing
import zeit.workflow.testing


@shared_task(urgency='homepage')
def hp_task():
    """Task with urgency homepage."""


@shared_task()
def no_default_urgency():
    """Task without a default urgency."""


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

    def test_route_task__returns_queue_of_default_priority_if_no_urgency(self):
        assert 'default' == self.get_queue_name(no_default_urgency)

    def test_route_task__returns_queue_depending_on_urgency_set_on_task(self):
        assert 'homepage' == self.get_queue_name(hp_task)

    def test_route_task__returns_queue_depending_on_urgency_set_on_call(self):
        assert ('highprio' ==
                self.get_queue_name(no_default_urgency, urgency='highprio'))

    def test_route_task__priorizes_call_over_task_setting(self):
        assert 'lowprio' == self.get_queue_name(hp_task, urgency='lowprio')
