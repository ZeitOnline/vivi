import pendulum
import transaction

from zeit.workflow.scheduled.interfaces import IScheduledOperations
import zeit.cms.metrics
import zeit.cms.workflow.interfaces
import zeit.workflow.testing


class ContentNotRetractedCountTest(zeit.workflow.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        zeit.cms.metrics.REGISTRY._collector_to_names.clear()
        zeit.cms.metrics.REGISTRY._names_to_collectors.clear()

        self.content = self.repository['testcontent']
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.urgent = True
        publish = zeit.cms.workflow.interfaces.IPublish(self.content)
        publish.publish(background=False)
        transaction.commit()

    def test_reports_zero_when_no_overdue_retractions(self):
        zeit.cms.metrics._collect_content_not_retracted_count()

        metric = zeit.cms.metrics.REGISTRY.get_sample_value(
            'vivi_content_not_retracted_total', labels={'environment': 'testing'}
        )
        self.assertEqual(0, metric)

    def test_reports_zero_when_retraction_not_overdue(self):
        ops = IScheduledOperations(self.content)
        ops.add('retract', pendulum.now('UTC').add(hours=1))
        transaction.commit()

        zeit.cms.metrics._collect_content_not_retracted_count()

        metric = zeit.cms.metrics.REGISTRY.get_sample_value(
            'vivi_content_not_retracted_total', labels={'environment': 'testing'}
        )
        self.assertEqual(0, metric)

    def test_reports_one_when_retraction_overdue(self):
        ops = IScheduledOperations(self.content)
        ops.add('retract', pendulum.now('UTC').add(minutes=-31))
        transaction.commit()

        zeit.cms.metrics._collect_content_not_retracted_count()

        metric = zeit.cms.metrics.REGISTRY.get_sample_value(
            'vivi_content_not_retracted_total', labels={'environment': 'testing'}
        )
        self.assertEqual(1, metric)

    def test_ignores_already_executed_retractions(self):
        ops = IScheduledOperations(self.content)
        ops.add('retract', pendulum.now('UTC').add(minutes=-31))
        transaction.commit()

        publish = zeit.cms.workflow.interfaces.IPublish(self.content)
        publish.retract(background=False)
        transaction.commit()

        zeit.cms.metrics._collect_content_not_retracted_count()

        metric = zeit.cms.metrics.REGISTRY.get_sample_value(
            'vivi_content_not_retracted_total', labels={'environment': 'testing'}
        )
        self.assertEqual(0, metric)

    def test_ignores_unpublished_content(self):
        publish = zeit.cms.workflow.interfaces.IPublish(self.content)
        publish.retract(background=False)
        transaction.commit()

        ops = IScheduledOperations(self.content)
        ops.add('retract', pendulum.now('UTC').add(minutes=-31))
        transaction.commit()

        zeit.cms.metrics._collect_content_not_retracted_count()

        metric = zeit.cms.metrics.REGISTRY.get_sample_value(
            'vivi_content_not_retracted_total', labels={'environment': 'testing'}
        )
        self.assertEqual(0, metric)

    def test_ignores_publish_operations(self):
        """Only retract operations should be counted, not publish operations."""
        ops = IScheduledOperations(self.content)
        ops.add('publish', pendulum.now('UTC').add(minutes=-31))
        transaction.commit()

        zeit.cms.metrics._collect_content_not_retracted_count()

        metric = zeit.cms.metrics.REGISTRY.get_sample_value(
            'vivi_content_not_retracted_total', labels={'environment': 'testing'}
        )
        self.assertEqual(0, metric)
