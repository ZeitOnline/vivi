from io import StringIO
from unittest import mock
import logging

import celery.result
import celery_longterm_scheduler
import pendulum
import transaction
import zope.component
import zope.i18n

from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
import zeit.cms.testing
import zeit.workflow.testing

from ..timebased import TimeBasedWorkflow


class TimeBasedWorkflowTest(zeit.workflow.testing.FunctionalTestCase):
    def test_should_schedule_job_for_renamed_uniqueId(self):
        with (
            mock.patch('zeit.cms.celery.Task.apply_async') as apply_async,
            checked_out(self.repository['testcontent']) as co,
        ):
            rn = zeit.cms.repository.interfaces.IAutomaticallyRenameable(co)
            rn.renameable = True
            rn.rename_to = 'changed'
            workflow = zeit.cms.workflow.interfaces.IPublishInfo(co)
            workflow.release_period = (pendulum.now('UTC').add(days=1), None)
            transaction.commit()
            self.assertEqual('http://xml.zeit.de/changed', apply_async.call_args[0][0][0][0])


class TimeBasedCeleryEndToEndTest(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.CELERY_LAYER

    def setUp(self):
        super().setUp()
        self.unique_id = 'http://xml.zeit.de/online/2007/01/Somalia'
        self.content = ICMSContent(self.unique_id)
        self.workflow = zeit.workflow.interfaces.IContentWorkflow(self.content)
        self.workflow.urgent = True
        self.log = StringIO()
        self.handler = logging.StreamHandler(self.log)
        logging.root.addHandler(self.handler)
        self.loggers = [None, 'zeit']
        self.oldlevels = {}
        for name in self.loggers:
            log = logging.getLogger(name)
            self.oldlevels[name] = log.level
            log.setLevel(logging.INFO)

    def tearDown(self):
        logging.root.removeHandler(self.handler)
        for name in self.loggers:
            logging.getLogger(name).setLevel(self.oldlevels[name])
        super().tearDown()

    def test_time_based_workflow_basic_assumptions(self):
        assert not self.workflow.published
        assert (None, None) == self.workflow.release_period
        assert 'can-publish-success' == self.workflow.can_publish()

    def test_released_from__in_past_is_published_instantly(self):
        publish_on = pendulum.now('UTC').add(seconds=-1)

        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        # Make sure the task is completed before asserting its output:
        assert 'Published.' == result.get()

        self.assertEllipsis(
            """\
...
Running job {0.workflow.publish_job_id} for http://xml.zeit.de/online/2007/01/Somalia
Publishing http://xml.zeit.de/online/2007/01/Somalia...""".format(self),  # noqa
            self.log.getvalue(),
        )

    def test_released_from__in_future_is_published_later(self):
        publish_on = pendulum.now('UTC').add(seconds=1.2)

        self.workflow.release_period = (publish_on, None)
        transaction.commit()

        scheduler = celery_longterm_scheduler.get_scheduler(self.layer['celery_app'])
        scheduler.execute_pending(publish_on)
        transaction.commit()

        result = celery.result.AsyncResult(self.workflow.publish_job_id)
        assert 'Published.' == result.get()
        self.assertEllipsis(
            """\
Start executing tasks...
Enqueuing...
Revoked...
End executing tasks...
Running job {0.workflow.publish_job_id} for http://xml.zeit.de/online/2007/01/Somalia
Publishing http://xml.zeit.de/online/2007/01/Somalia...""".format(self),  # noqa
            self.log.getvalue(),
        )

    def test_released_from__revokes_job_on_change(self):
        publish_on = pendulum.now('UTC').add(days=1)

        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        job_id = self.workflow.publish_job_id
        scheduler = celery_longterm_scheduler.get_scheduler(self.layer['celery_app'])
        assert scheduler.backend.get(job_id)

        # The current job gets revoked on change of released_from:
        publish_on = publish_on.add(seconds=1)
        self.workflow.release_period = (publish_on, None)
        transaction.commit()
        with self.assertRaises(KeyError):
            scheduler.backend.get(job_id)

        # The newly created job is pending its execution:
        new_job = self.workflow.publish_job_id
        assert scheduler.backend.get(new_job)

    def test_released_from__revokes_job_on_change_while_checked_out(self):
        publish_on = pendulum.now('UTC').add(days=1)

        with checked_out(self.content) as co:
            workflow = zeit.cms.workflow.interfaces.IPublishInfo(co)
            workflow.release_period = (publish_on, None)
        transaction.commit()
        job_id = self.workflow.publish_job_id
        scheduler = celery_longterm_scheduler.get_scheduler(self.layer['celery_app'])
        assert scheduler.backend.get(job_id)

        # The current job gets revoked on change of released_from:
        publish_on = publish_on.add(seconds=1)
        with checked_out(self.content) as co:
            workflow = zeit.cms.workflow.interfaces.IPublishInfo(co)
            workflow.release_period = (publish_on, None)
        transaction.commit()
        with self.assertRaises(KeyError):
            scheduler.backend.get(job_id)

        # The newly created job is pending its execution:
        new_job = self.workflow.publish_job_id
        assert scheduler.backend.get(new_job)

    def test_released_to__in_past_retracts_instantly(self):
        zeit.cms.workflow.interfaces.IPublish(self.content).publish(background=False)
        transaction.commit()

        retract_on = pendulum.now('UTC').add(seconds=-1)
        self.workflow.release_period = (None, retract_on)
        transaction.commit()

        result = celery.result.AsyncResult(self.workflow.retract_job_id)
        # Make sure the task is completed before asserting its output:
        assert 'Retracted.' == result.get()

        self.assertEllipsis(
            """...
Running job {0.workflow.retract_job_id} for http://xml.zeit.de/online/2007/01/Somalia
Retracting http://xml.zeit.de/online/2007/01/Somalia...""".format(self),  # noqa
            self.log.getvalue(),
        )

    def test_released_to__in_future_is_retracted_later(self):
        zeit.cms.workflow.interfaces.IPublish(self.content).publish(background=False)
        transaction.commit()

        retract_on = pendulum.now('UTC').add(seconds=1.5)
        self.workflow.release_period = (None, retract_on)
        transaction.commit()
        cancel_retract_job_id = self.workflow.retract_job_id
        scheduler = celery_longterm_scheduler.get_scheduler(self.layer['celery_app'])
        assert scheduler.backend.get(cancel_retract_job_id)

        # The current job gets revoked on change of released_to:
        new_retract_on = retract_on.add(seconds=1)
        self.workflow.release_period = (None, new_retract_on)
        transaction.commit()
        with self.assertRaises(KeyError):
            scheduler.backend.get(cancel_retract_job_id)

        # The newly created job is pending its execution:
        new_job = self.workflow.retract_job_id
        assert scheduler.backend.get(new_job)

        # The actions are logged:
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log_entries = [zope.i18n.translate(e.message) for e in log.get_log(self.content)]

        def berlin(dt):
            return TimeBasedWorkflow.format_datetime(dt)

        self.assertEqual(
            [
                'Urgent: yes',
                'Published',
                'To retract on {} (job #{})'.format(berlin(retract_on), cancel_retract_job_id),
                'Scheduled retract cancelled (job #{}).'.format(cancel_retract_job_id),
                'To retract on {} (job #{})'.format(
                    berlin(new_retract_on), self.workflow.retract_job_id
                ),
            ],
            log_entries,
        )
