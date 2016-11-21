from ..celery import ActiveInteractionError
import datetime
import mock
import transaction
import zeit.cms.celery
import zeit.cms.testing
import zope.security.management


@zeit.cms.celery.task()
def dummy_task(context=None, datetime=None):
    """Dummy task to test our framework."""


@zeit.cms.celery.task()
def get_principal_title_task():
    """Task returning the principal's title used to run it."""
    interaction = zope.security.management.getInteraction()
    return interaction.participations[0].principal.title


class CeleryTaskTest(zeit.cms.testing.ZeitCmsTestCase):
    """Testing ..celery.TransactionAwareTask."""

    def test_registering_task_without_json_serializable_arguments_raises(self):
        now = datetime.datetime.now()
        with self.assertRaises(TypeError):
            dummy_task.delay(self.repository['testcontent'], datetime=now)
        with self.assertRaises(TypeError):
            dummy_task.apply_async(
                (self.repository['testcontent'],), {'datetime': now},
                task_id=now, countdown=now)

    def test_registering_task_with_json_serializable_argument_passes(self):
        with self.assertNothingRaised():
            dummy_task.delay('http://xml.zeit.de/testcontent',
                             datetime='2016-01-01 12:00:00')
            dummy_task.apply_async(
                ('http://xml.zeit.de/testcontent',),
                {'datetime': '2016-01-01 12:00:00'},
                task_id=1, countdown=30)

    def test___call___expects_that_no_interaction_runs_for_async_tasks(self):
        with self.assertRaises(ActiveInteractionError):
            dummy_task(_run_asynchronously_=True, _principal_id_='zope.user')
        zope.security.management.endInteraction()
        with self.assertNothingRaised():
            dummy_task(_run_asynchronously_=True, _principal_id_='zope.user')

    def test_delay_extracts_principal_from_interaction_if_async(self):
        with mock.patch.dict(dummy_task.app.conf,
                             {'CELERY_ALWAYS_EAGER': False}):
            dummy_task.delay('1st param', datetime='now()')
        task_call = 'zeit.cms.celery.TransactionAwareTask.__call__'
        with mock.patch(task_call) as task_call:
            zope.security.management.endInteraction()
            transaction.commit()
        task_call.assert_called_with(
            '1st param', datetime='now()',
            _run_asynchronously_=True, _principal_id_=u'zope.user')

    def test_apply_async_extracts_principal_from_interaction_if_async(self):
        with mock.patch.dict(dummy_task.app.conf,
                             {'CELERY_ALWAYS_EAGER': False}):
            dummy_task.apply_async(('1st param',), dict(datetime='now()'))
        task_call = 'zeit.cms.celery.TransactionAwareTask.__call__'
        with mock.patch(task_call) as task_call:
            zope.security.management.endInteraction()
            transaction.commit()
        task_call.assert_called_with(
            '1st param', datetime='now()',
            _run_asynchronously_=True, _principal_id_=u'zope.user')

    def test___call___runs_async_task_as_given_principal(self):
        auth = zope.component.getUtility(
            zope.app.security.interfaces.IAuthentication)
        auth.definePrincipal('<me>', 'Ikke')
        zope.security.management.endInteraction()

        result = get_principal_title_task(
            _run_asynchronously_=True, _principal_id_='<me>')
        assert 'Ikke' == result
