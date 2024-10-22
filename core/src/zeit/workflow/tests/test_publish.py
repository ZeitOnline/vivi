from io import StringIO
from unittest import mock
import json
import logging

from pendulum import datetime
from ZODB.POSException import ConflictError
import gocept.testing.mock
import pendulum
import requests_mock
import transaction
import z3c.celery.celery
import zope.component
import zope.i18n

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import IUUID
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import ICMSContent
from zeit.cms.related.interfaces import IRelatedContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.testing import CommitExceptionDataManager
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
import zeit.cms.config
import zeit.cms.related.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.interfaces
import zeit.workflow.publish
import zeit.workflow.publisher
import zeit.workflow.testing


class PublishTest(zeit.workflow.testing.FunctionalTestCase):
    def test_object_already_checked_out_should_raise(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        zeit.cms.checkout.interfaces.ICheckoutManager(article).checkout()
        zope.security.management.endInteraction()
        with zeit.cms.testing.interaction('zope.producer'):
            with self.assertRaises(Exception) as info:
                IPublish(article).publish(background=False)
            self.assertIn('LockingError', str(info.exception))
        self.assertEqual(False, IPublishInfo(article).published)

    def test_safetybelt_object_with_can_publish_false_is_not_published(self):
        # can_publish was already checked in IPublish.publish(), we make sure
        # the state has not changed by the time the actual publish task runs.
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        with self.assertRaises(Exception) as info:
            zeit.workflow.publish.PUBLISH_TASK([article.uniqueId])
            assert 'PublishError' in str(info.exception)
        self.assertEqual(False, IPublishInfo(article).published)

    def test_serialize_error_still_publishes_other_items(self):
        c1 = ICMSContent('http://xml.zeit.de/online/2007/01/Flugsicherheit')
        c2 = ICMSContent('http://xml.zeit.de/online/2007/01/Saarland')
        IPublishInfo(c1).urgent = True
        IPublishInfo(c2).urgent = True

        @zope.component.adapter(zeit.cms.interfaces.ICMSContent)
        @zope.interface.implementer(zeit.workflow.interfaces.IPublisherData)
        class FailingPublisherData:
            def __init__(self, context):
                self.context = context

            def publish_json(self):
                if self.context.uniqueId == c1.uniqueId:
                    raise RuntimeError('provoked')
                return {}

        zope.component.getGlobalSiteManager().registerAdapter(FailingPublisherData, name='test')
        with self.assertRaises(Exception) as err:
            # DAV doesn't have transactions, so setting published=True in before_publish
            # (which is needed so e.g. TMS gets the correct properties)
            # is not rolled back when an error occurs in the later serialize step.
            # Apart from being not really correct in general
            # (but it's "always" been like that, so the impact can't have been very high),
            # this prevents us from simply asserting `IPublishInfo(c1).published == False`
            with mock.patch('zeit.workflow.publisher.MockPublisher.request') as publisher:
                IPublish(c1).publish_multiple([c1, c2])
                self.assertIn('provoked', str(err.exception))
                items = publisher.call_args[0][0]
                self.assertEqual(1, len(items))
                self.assertEqual(c2.uniqueId, items[0]['uniqueId'])

    def test_conflict_error_on_commit_is_raised(self):
        FEATURE_TOGGLES.set('publish_commit_transaction')

        def provoke_conflict(*args, **kw):
            transaction.get().join(CommitExceptionDataManager(ConflictError()))

        zope.component.getGlobalSiteManager().registerHandler(
            provoke_conflict, (zeit.cms.workflow.interfaces.IBeforePublishEvent,)
        )

        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True

        with self.assertRaises(ConflictError):
            IPublish(article).publish(background=False)


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublicationDependencies)
class RelatedDependency:
    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        relateds = zeit.cms.related.interfaces.IRelatedContent(self.context)
        return relateds.related


class PublicationDependencies(zeit.workflow.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.patches = gocept.testing.mock.Patches()
        self.populate_repository_with_dummy_content()
        self.setup_dates_so_content_is_publishable()
        zeit.cms.config.set('zeit.workflow', 'dependency-publish-limit', 2)
        zope.component.getSiteManager().registerAdapter(RelatedDependency, name='related')

    def tearDown(self):
        self.patches.reset()
        zope.component.getSiteManager().unregisterAdapter(RelatedDependency, name='related')
        super().tearDown()

    def populate_repository_with_dummy_content(self):
        self.related = []
        for i in range(3):
            item = ExampleContentType()
            self.repository['t%s' % i] = item
            self.related.append(self.repository['t%s' % i])

    def setup_dates_so_content_is_publishable(self):
        DAY1 = datetime(2010, 1, 1)
        DAY2 = datetime(2010, 2, 1)
        DAY3 = datetime(2010, 3, 1)

        # XXX it would be nicer to patch this just for the items in question,
        # but we lack the mechanics to easily substitute adapter instances
        sem = self.patches.add('zeit.cms.content.interfaces.ISemanticChange')
        sem().last_semantic_change = DAY1
        sem().has_semantic_change = False
        for item in self.related:
            info = IPublishInfo(item)
            info.published = True
            info.date_last_published = DAY2
        mod = self.patches.add('zeit.cms.workflow.interfaces.IModified')
        mod().date_last_modified = DAY3

    def publish(self, content):
        IPublishInfo(content).urgent = True
        IPublish(content).publish(background=False)

    def test_should_not_publish_more_dependencies_than_the_limit_breadth(self):
        content = self.repository['testcontent']
        with checked_out(content) as co:
            IRelatedContent(co).related = tuple(self.related)
        for item in self.related:
            info = IPublishInfo(item)
            info.urgent = True

        BEFORE_PUBLISH = pendulum.now('UTC')
        self.publish(content)

        self.assertEqual(
            2,
            len([x for x in self.related if IPublishInfo(x).date_last_published > BEFORE_PUBLISH]),
        )

    def test_should_not_publish_more_dependencies_than_the_limit_depth(self):
        content = [self.repository['testcontent']] + self.related
        for i in range(3):
            with checked_out(content[i]) as co:
                IRelatedContent(co).related = (content[i + 1],)
        for item in self.related:
            info = IPublishInfo(item)
            info.urgent = True
        BEFORE_PUBLISH = pendulum.now('UTC')
        self.publish(content[0])

        self.assertEqual(
            2,
            len([x for x in self.related if IPublishInfo(x).date_last_published > BEFORE_PUBLISH]),
        )


class SynchronousPublishTest(zeit.workflow.testing.FunctionalTestCase):
    def test_publish_and_retract_in_same_process(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        info = IPublishInfo(article)
        info.urgent = True
        publish = IPublish(article)
        self.assertFalse(info.published)
        publish.publish(background=False)
        self.assertTrue(info.published)
        publish.retract(background=False)
        self.assertFalse(info.published)

        logs = reversed(zeit.objectlog.interfaces.ILog(article).logs)
        self.assertEqual(
            ['${name}: ${new_value}', 'Published', 'Retracted'], [x.message for x in logs]
        )

    def test_synchronous_multi_publishing_works_with_unique_ids(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        info = IPublishInfo(article)
        info.urgent = True
        IPublish(article).publish(background=False)
        self.assertTrue(info.published)
        IPublish(article).retract_multiple([article.uniqueId], background=True)
        self.assertFalse(info.published)

    def test_ignores_invalid_unique_ids(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        info = IPublishInfo(article)
        info.urgent = True
        zeit.workflow.publish.PUBLISH_TASK(['http://xml.zeit.de/nonexistent', article.uniqueId])
        self.assertTrue(info.published)


class PublishPriorityTest(zeit.workflow.testing.FunctionalTestCase):
    def test_determines_priority_via_adapter(self):
        content = self.repository['testcontent']
        info = IPublishInfo(content)
        info.urgent = True
        self.assertFalse(info.published)
        with (
            mock.patch('zeit.cms.workflow.interfaces.IPublishPriority') as priority,
            mock.patch.object(zeit.workflow.publish.PUBLISH_TASK, 'apply_async') as apply_async,
        ):
            priority.return_value = zeit.cms.workflow.interfaces.PRIORITY_LOW
            IPublish(content).publish()
        apply_async.assert_called_with(
            (['http://xml.zeit.de/testcontent'], None), queue='publish_lowprio'
        )


def get_object_log(obj):
    log = zeit.objectlog.interfaces.ILog(obj)
    return [x.message for x in log.get_log()]


def translate_object_log(obj):
    return [zope.i18n.interpolate(x, x.mapping) for x in get_object_log(obj)]


class PublishEndToEndTest(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.CELERY_LAYER

    def setUp(self):
        super().setUp()
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

    def test_publish_via_celery_end_to_end(self):
        content = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        info = IPublishInfo(content)
        self.assertFalse(info.published)
        info.urgent = True

        publish = IPublish(content).publish()
        transaction.commit()
        self.assertEqual('Published.', publish.get())
        transaction.begin()

        self.assertEllipsis(
            """\
...
Publishing http://xml.zeit.de/online/2007/01/Somalia...
Task zeit.workflow.publish.PUBLISH_TASK...succeeded...""",
            self.log.getvalue(),
        )
        self.assertIn('Published', get_object_log(content))

    def test_publish_multiple_via_celery_end_to_end(self):
        context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Querdax')
        c1 = ICMSContent('http://xml.zeit.de/online/2007/01/Flugsicherheit')
        c2 = ICMSContent('http://xml.zeit.de/online/2007/01/Saarland')
        i1 = IPublishInfo(c1)
        i2 = IPublishInfo(c2)
        self.assertFalse(i1.published)
        self.assertFalse(i2.published)
        i1.urgent = True
        i2.urgent = True

        publish = IPublish(context).publish_multiple([c1, c2])
        transaction.commit()
        self.assertEqual(len(publish), 2)
        self.assertTrue(all('Published.' == p.get() for p in publish))
        transaction.begin()
        self.assertEllipsis(
            """\
...
Running job...for http://xml.zeit.de/online/2007/01/Flugsicherheit
Publishing http://xml.zeit.de/online/2007/01/Flugsicherheit...
Task zeit.workflow.publish.PUBLISH_TASK...succeeded...
Running job...for http://xml.zeit.de/online/2007/01/Saarland
Publishing http://xml.zeit.de/online/2007/01/Saarland...
Task zeit.workflow.publish.PUBLISH_TASK...succeeded...""",
            self.log.getvalue(),
        )

        self.assertIn('Published', get_object_log(c1))
        self.assertIn('Published', get_object_log(c2))

    def test_publish_multiple_continues_if_tasks_fail(self):
        def after_publish(context, event):
            if context.uniqueId == c1.uniqueId:
                raise RuntimeError('provoked')

        zope.component.getGlobalSiteManager().registerHandler(
            after_publish,
            (zeit.cms.interfaces.ICMSContent, zeit.cms.workflow.interfaces.IPublishedEvent),
        )
        context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Querdax')
        c1 = ICMSContent('http://xml.zeit.de/online/2007/01/Flugsicherheit')
        c2 = ICMSContent('http://xml.zeit.de/online/2007/01/Saarland')
        i1 = IPublishInfo(c1)
        i2 = IPublishInfo(c2)
        self.assertFalse(i1.published)
        self.assertFalse(i2.published)
        i1.urgent = True
        i2.urgent = True

        publish = IPublish(context).publish_multiple([c1, c2])
        transaction.commit()
        self.assertEqual(len(publish), 2)
        with self.assertRaises(z3c.celery.celery.HandleAfterAbort):
            publish[0].get()
        publish[1].get()
        transaction.begin()
        self.assertIn('Error during publish/retract: ${exc}: ${message}', get_object_log(c1))
        self.assertIn('Published', get_object_log(c2))
        self.assertIn('Objects with errors: ${objects}', get_object_log(context))


class PublishErrorTest(zeit.workflow.testing.FunctionalTestCase):
    message = 'Error during publish/retract: PublishError: '

    def setUp(self):
        super().setUp()
        self.patch = mock.patch('zeit.workflow.publisher.MockPublisher.request')
        self.publisher = self.patch.start()

        self.content = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(self.content).urgent = True

        self.publisher.side_effect = zeit.workflow.publisher.PublisherError(
            'testing',
            500,
            [
                {
                    'status': 500,
                    'title': 'Subsystem',
                    'detail': 'Provoked',
                    'source': {'pointer': IUUID(self.content).shortened},
                }
            ],
        )

    def tearDown(self):
        self.patch.stop()
        super().tearDown()

    def test_publisher_errors_are_written_to_objectlog(self):
        with self.assertRaises(Exception):
            IPublish(self.content).publish(background=False)
        self.assertEqual(
            'testing returned 500, Details: ' + json.dumps(self.publisher.side_effect.errors),
            translate_object_log(self.content)[-1].replace(self.message, ''),
        )

    def test_publisher_errors_multi_are_assigned_to_source_object(self):
        main = ICMSContent('http://xml.zeit.de/online/2007/01/Querdax')
        IPublishInfo(main).urgent = True
        self.publisher.side_effect.errors.append(
            {'title': 'Unrelated', 'source': {'pointer': IUUID(main).shortened}}
        )
        with self.assertRaises(Exception):
            IPublish(main).retract_multiple([self.content, main], background=False)
        log = translate_object_log(self.content)[-1].replace(self.message, '')
        self.assertEqual('testing returned 500: Subsystem (500), Details: Provoked', log)
        self.assertNotIn('Unrelated', log)

    def test_publisher_errors_multi_writes_summary_on_original_object(self):
        main = ICMSContent('http://xml.zeit.de/online/2007/01/Querdax')
        IPublishInfo(main).urgent = True
        self.publisher.side_effect.errors.append(
            {'title': 'Unrelated', 'source': {'pointer': IUUID(main).shortened}}
        )
        with self.assertRaises(Exception):
            IPublish(main).publish_multiple([self.content, main])
        self.assertEqual(
            f'Objects with errors: {self.content.uniqueId}',
            translate_object_log(main)[-1].replace(self.message, ''),
        )


class PublishErrorEndToEndTest(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.CELERY_LAYER
    error = 'Error during publish/retract: PublishError: http://publisher.testing returned 678'

    def setUp(self):
        self.publisher = mock.patch('zeit.workflow.publisher.MockPublisher.request')
        self.mocker = self.publisher.start()
        self.mocker.side_effect = zeit.workflow.publisher.PublisherError(
            'http://publisher.testing', 678, []
        )
        super().setUp()

    def tearDown(self):
        self.publisher.stop()
        super().tearDown()

    def test_error_during_publish_is_written_to_objectlog(self):
        content = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        info = IPublishInfo(content)
        self.assertFalse(info.published)
        info.urgent = True

        publish = IPublish(content).publish()
        transaction.commit()

        with self.assertRaises(Exception) as err:
            publish.get()
        transaction.begin()

        self.assertIn('678', str(err.exception))
        self.assertIn(self.error, translate_object_log(content))

    def test_error_during_publish_multiple_is_written_to_objectlog(self):
        c1 = ICMSContent('http://xml.zeit.de/online/2007/01/Flugsicherheit')
        c2 = ICMSContent('http://xml.zeit.de/online/2007/01/Saarland')
        c3 = ICMSContent('http://xml.zeit.de/online/2007/01/Querdax')
        i1 = IPublishInfo(c1)
        i2 = IPublishInfo(c2)
        i3 = IPublishInfo(c3)
        self.assertFalse(i1.published)
        self.assertFalse(i2.published)
        self.assertFalse(i3.published)
        i1.urgent = True
        i2.urgent = True
        i3.urgent = True

        zope.security.management.endInteraction()
        with zeit.cms.testing.interaction('zope.producer'):
            zeit.cms.checkout.interfaces.ICheckoutManager(c3).checkout()
            transaction.commit()
        zeit.cms.testing.create_interaction('zope.user')

        publish = IPublish(c1).publish_multiple([c1, c2, c3])
        transaction.commit()

        self.assertEqual(len(publish), 3)
        with self.assertRaises(Exception) as err:
            publish.pop(0).get()
        self.assertIn('678', str(err.exception))
        for job in publish:
            with self.assertRaises(Exception):
                job.get()
        transaction.begin()

        self.assertIn(self.error, translate_object_log(c1))
        self.assertIn(self.error, translate_object_log(c2))
        self.assertIn('LockingError', translate_object_log(c3)[-1])
        log_messages = translate_object_log(c1)
        self.assertIn(
            'Objects with errors: http://xml.zeit.de/online/2007/01/Flugsicherheit',
            log_messages,
        )
        self.assertIn(
            'Objects with errors: http://xml.zeit.de/online/2007/01/Saarland',
            log_messages,
        )
        self.assertIn(
            'Objects with errors: http://xml.zeit.de/online/2007/01/Querdax',
            log_messages,
        )


class MultiPublishRetractTest(zeit.workflow.testing.FunctionalTestCase):
    def test_publishes_and_retracts_multiple_objects_in_single_call(self):
        c1 = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        c2 = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/eta-zapatero')
        IPublishInfo(c1).urgent = True
        IPublishInfo(c2).urgent = True
        IPublish(self.repository).publish_multiple([c1, c2])
        self.assertTrue(IPublishInfo(c1).published)
        self.assertTrue(IPublishInfo(c2).published)
        IPublish(self.repository).retract_multiple([c1, c2])
        self.assertFalse(IPublishInfo(c1).published)
        self.assertFalse(IPublishInfo(c2).published)

    def test_accepts_uniqueId_as_well_as_ICMSContent(self):
        with mock.patch('zeit.workflow.publish.PublishTask.run') as run:
            c1 = self.repository['testcontent']
            c2 = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
            IPublishInfo(c1).urgent = True
            IPublishInfo(c2).urgent = True
            IPublish(self.repository).publish_multiple(
                [c1, 'http://xml.zeit.de/online/2007/01/Somalia'],
            )
            run.assert_any_call([c1.uniqueId], self.repository.uniqueId)
            run.assert_any_call([c2.uniqueId], self.repository.uniqueId)

    def test_empty_list_of_objects_does_not_run_publish(self):
        with mock.patch('zeit.workflow.publisher.Publisher.request') as publish:
            IPublish(self.repository).publish_multiple([])
            self.assertFalse(publish.called)


class NewPublisherTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.workflow.testing.ARTICLE_LAYER

    def setUp(self):
        super().setUp()
        self.gsm = zope.component.getGlobalSiteManager()
        self.gsm.registerUtility(
            zeit.workflow.publisher.Publisher(), zeit.cms.workflow.interfaces.IPublisher
        )

    def test_object_is_published(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            self.assertEqual('http://xml.zeit.de/online/2007/01/Somalia', result['uniqueId'])
            self.assertIn('uuid', result)
        self.assertTrue(IPublishInfo(article).published)

    def test_object_is_retracted(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        IPublishInfo(article).published = True
        self.assertTrue(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post('http://localhost:8060/test/retract', status_code=200)
            IPublish(article).retract(background=False)
            (result,) = response.last_request.json()
            self.assertEqual('http://xml.zeit.de/online/2007/01/Somalia', result['uniqueId'])
            self.assertIn('uuid', result)
        self.assertFalse(IPublishInfo(article).published)
