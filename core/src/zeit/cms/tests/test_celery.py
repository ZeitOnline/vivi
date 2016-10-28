import datetime
import zeit.cms.celery
import zeit.cms.testing


@zeit.cms.celery.CELERY.task()
def task(context, datetime):
    pass


class CeleryTaskTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_registering_task_without_json_serializable_arguments_raises(self):
        now = datetime.datetime.now()
        with self.assertRaises(TypeError):
            task.delay(self.repository['testcontent'], datetime=now)
        with self.assertRaises(TypeError):
            task.apply_async(
                (self.repository['testcontent'],), {'datetime': now},
                task_id=now, countdown=now)

    def test_registering_task_with_json_serializable_argument_passes(self):
        with self.assertNothingRaised():
            task.delay('http://xml.zeit.de/testcontent',
                       datetime='2016-01-01 12:00:00')
            task.apply_async(
                ('http://xml.zeit.de/testcontent',),
                {'datetime': '2016-01-01 12:00:00'},
                task_id=1, countdown=30)
