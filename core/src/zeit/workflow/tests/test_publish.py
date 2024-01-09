from datetime import datetime
from io import StringIO
from unittest import mock
import json
import logging
import time

import gocept.testing.mock
import pytz
import requests_mock
import transaction
import zope.app.appsetup.product
import zope.component
import zope.i18n

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import IUUID
from zeit.cms.interfaces import ICMSContent
from zeit.cms.related.interfaces import IRelatedContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
import zeit.cms.related.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.content.article.testing
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


class FakePublishTask(zeit.workflow.publish.PublishRetractTask):
    def __init__(self):
        self.test_log = []

    def _run(self, obj):
        time.sleep(0.1)
        self.test_log.append(obj)

    @property
    def jobid(self):
        return None


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
        self.patches.add_dict(
            zope.app.appsetup.product.getProductConfiguration('zeit.workflow'),
            {'dependency-publish-limit': 2},
        )
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
        DAY1 = datetime(2010, 1, 1, tzinfo=pytz.UTC)
        DAY2 = datetime(2010, 2, 1, tzinfo=pytz.UTC)
        DAY3 = datetime(2010, 3, 1, tzinfo=pytz.UTC)

        # XXX it would be nicer to patch this just for the items in question,
        # but we lack the mechanics to easily substitute adapter instances
        sem = self.patches.add('zeit.cms.content.interfaces.ISemanticChange')
        sem().last_semantic_change = DAY1
        sem().has_semantic_change = False
        for item in self.related:
            info = IPublishInfo(item)
            info.published = True
            info.date_last_published = DAY2
        dc = self.patches.add('zope.dublincore.interfaces.IDCTimes')
        dc().modified = DAY3

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

        BEFORE_PUBLISH = datetime.now(pytz.UTC)
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
        BEFORE_PUBLISH = datetime.now(pytz.UTC)
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
        IPublish(article).publish_multiple([article.uniqueId], background=False)
        self.assertTrue(info.published)

    def test_ignores_invalid_unique_ids(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        info = IPublishInfo(article)
        info.urgent = True
        zeit.workflow.publish.MULTI_PUBLISH_TASK(
            ['http://xml.zeit.de/nonexistent', article.uniqueId]
        )
        self.assertTrue(info.published)


class PublishPriorityTest(zeit.workflow.testing.FunctionalTestCase):
    def test_determines_priority_via_adapter(self):
        content = self.repository['testcontent']
        info = IPublishInfo(content)
        info.urgent = True
        self.assertFalse(info.published)
        with mock.patch(
            'zeit.cms.workflow.interfaces.IPublishPriority'
        ) as priority, mock.patch.object(
            zeit.workflow.publish.PUBLISH_TASK, 'apply_async'
        ) as apply_async:
            priority.return_value = zeit.cms.workflow.interfaces.PRIORITY_LOW
            IPublish(content).publish()
        apply_async.assert_called_with(
            (['http://xml.zeit.de/testcontent'],), queue='publish_lowprio'
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
Publishing http://xml.zeit.de/online/2007/01/Somalia
Done http://xml.zeit.de/online/2007/01/Somalia (...s)...""",
            self.log.getvalue(),
        )
        self.assertIn('Published', get_object_log(content))

    def test_publish_multiple_via_celery_end_to_end(self):
        c1 = ICMSContent('http://xml.zeit.de/online/2007/01/Flugsicherheit')
        c2 = ICMSContent('http://xml.zeit.de/online/2007/01/Saarland')
        i1 = IPublishInfo(c1)
        i2 = IPublishInfo(c2)
        self.assertFalse(i1.published)
        self.assertFalse(i2.published)
        i1.urgent = True
        i2.urgent = True

        publish = IPublish(c1).publish_multiple([c1, c2])
        transaction.commit()
        self.assertEqual('Published.', publish.get())
        transaction.begin()
        self.assertEllipsis(
            """\
...
    for http://xml.zeit.de/online/2007/01/Flugsicherheit,
        http://xml.zeit.de/online/2007/01/Saarland
Publishing http://xml.zeit.de/online/2007/01/Flugsicherheit,
       http://xml.zeit.de/online/2007/01/Saarland
Done http://xml.zeit.de/online/2007/01/Flugsicherheit,
 http://xml.zeit.de/online/2007/01/Saarland (...s)...""",
            self.log.getvalue(),
        )

        self.assertIn('Published', get_object_log(c1))
        self.assertIn('Published', get_object_log(c2))


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
            IPublish(main).publish_multiple([self.content, main], background=False)
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
            IPublish(main).publish_multiple([self.content, main], background=False)
        self.assertEqual(
            f'Objects with errors: {main.uniqueId}, {self.content.uniqueId}',
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

        with self.assertRaises(Exception) as err:
            publish.get()
        transaction.begin()

        self.assertIn('678', str(err.exception))
        self.assertIn(self.error, translate_object_log(c1))
        self.assertIn(self.error, translate_object_log(c2))
        self.assertIn('LockingError', translate_object_log(c3)[-1])
        self.assertIn(
            'Objects with errors: '
            'http://xml.zeit.de/online/2007/01/Flugsicherheit, '
            'http://xml.zeit.de/online/2007/01/Querdax, '
            'http://xml.zeit.de/online/2007/01/Saarland',
            translate_object_log(c1),
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
        with mock.patch('zeit.workflow.publish.MultiPublishTask.run') as run:
            IPublish(self.repository).publish_multiple(
                [self.repository['testcontent'], 'http://xml.zeit.de/online/2007/01/Somalia'],
                background=False,
            )
            ids = run.call_args[0][0]
            self.assertEqual(
                [
                    'http://xml.zeit.de/',
                    'http://xml.zeit.de/testcontent',
                    'http://xml.zeit.de/online/2007/01/Somalia',
                ],
                ids,
            )

    def test_empty_list_of_objects_does_not_run_publish(self):
        with mock.patch('zeit.workflow.publisher.Publisher.request') as publish:
            IPublish(self.repository).publish_multiple([], background=False)
            self.assertFalse(publish.called)

    def test_error_in_one_item_continues_with_other_items(self):
        context = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Querdax')
        c1 = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        c2 = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/eta-zapatero')
        IPublishInfo(c1).urgent = True
        IPublishInfo(c2).urgent = True

        calls = []

        def after_publish(context, event):
            calls.append(context.uniqueId)
            if context.uniqueId == c1.uniqueId:
                raise RuntimeError('provoked')

        zope.component.getGlobalSiteManager().registerHandler(
            after_publish,
            (zeit.cms.interfaces.ICMSContent, zeit.cms.workflow.interfaces.IPublishedEvent),
        )

        with self.assertRaises(RuntimeError):
            IPublish(context).publish_multiple([c1, c2], background=False)

        # PublishedEvent still happens for c2, even though c1 raised
        self.assertIn(c2.uniqueId, calls)
        # Error is logged
        log = zeit.objectlog.interfaces.ILog(c1)
        self.assertEqual(
            [
                '${name}: ${new_value}',
                'Collective Publication of ${count} objects',
                'Error during publish/retract: ${exc}: ${message}',
            ],
            [x.message for x in log.get_log()],
        )


class NewPublisherTest(zeit.workflow.testing.FunctionalTestCase):
    layer = zeit.content.article.testing.LAYER

    def setUp(self):
        self.patch = mock.patch('zeit.retresco.interfaces.ITMSRepresentation')
        self.representation = self.patch.start()
        super().setUp()
        self.gsm = zope.component.getGlobalSiteManager()
        self.gsm.registerUtility(
            zeit.workflow.publisher.Publisher(), zeit.cms.workflow.interfaces.IPublisher
        )

    def tearDown(self):
        self.patch.stop()
        super().tearDown()

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
