from datetime import datetime
from io import StringIO
from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import ICMSContent
from zeit.cms.related.interfaces import IRelatedContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublishInfo, IPublish
import gocept.testing.mock
import logging
import os
import pytest
import pytz
import requests_mock
import shutil
import sys
import time
import transaction
import zeit.cms.related.interfaces
import zeit.cms.testing
import zeit.content.article.testing
import zeit.objectlog.interfaces
import zeit.workflow.interfaces
import zeit.workflow.publish
import zeit.workflow.publish_3rdparty
import zeit.workflow.testing
import zope.app.appsetup.product
import zope.component
import zope.i18n


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
@zope.interface.implementer(zeit.workflow.interfaces.IPublicationDependencies)
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
            {'dependency-publish-limit': 2})
        zope.component.getSiteManager().registerAdapter(
            RelatedDependency, name='related')

    def tearDown(self):
        self.patches.reset()
        zope.component.getSiteManager().unregisterAdapter(
            RelatedDependency, name='related')
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

        BEFORE_PUBLISH = datetime.now(pytz.UTC)
        self.publish(content)

        self.assertEqual(
            2, len([x for x in self.related
                    if IPublishInfo(x).date_last_published > BEFORE_PUBLISH]))

    def test_should_not_publish_more_dependencies_than_the_limit_depth(self):
        content = [self.repository['testcontent']] + self.related
        for i in range(3):
            with checked_out(content[i]) as co:
                IRelatedContent(co).related = tuple([content[i + 1]])

        BEFORE_PUBLISH = datetime.now(pytz.UTC)
        self.publish(content[0])

        self.assertEqual(
            2, len([x for x in self.related
                    if IPublishInfo(x).date_last_published > BEFORE_PUBLISH]))


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
            ['${name}: ${new_value}', 'Published', 'Retracted'],
            [x.message for x in logs])

    def test_synchronous_multi_publishing_works_with_unique_ids(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        info = IPublishInfo(article)
        info.urgent = True
        IPublish(article).publish_multiple(
            [article.uniqueId], background=False)
        self.assertTrue(info.published)

    def test_ignores_invalid_unique_ids(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        info = IPublishInfo(article)
        info.urgent = True
        zeit.workflow.publish.MULTI_PUBLISH_TASK(
            ['http://xml.zeit.de/nonexistent', article.uniqueId])
        self.assertTrue(info.published)


class PublishPriorityTest(zeit.workflow.testing.FunctionalTestCase):

    def test_determines_priority_via_adapter(self):
        content = self.repository['testcontent']
        info = IPublishInfo(content)
        info.urgent = True
        self.assertFalse(info.published)
        with mock.patch(
                'zeit.cms.workflow.interfaces.IPublishPriority') as priority,\
                mock.patch.object(zeit.workflow.publish.PUBLISH_TASK,
                                  'apply_async') as apply_async:
            priority.return_value = zeit.cms.workflow.interfaces.PRIORITY_LOW
            IPublish(content).publish()
        apply_async.assert_called_with(
            (['http://xml.zeit.de/testcontent'],),
            queue='publish_lowprio')


def get_object_log(obj):
    log = zeit.objectlog.interfaces.ILog(obj)
    return [x.message for x in log.get_log()]


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

        self.assertEllipsis("""\
...
Publishing http://xml.zeit.de/online/2007/01/Somalia
...
Done http://xml.zeit.de/online/2007/01/Somalia (...s)...""",
                            self.log.getvalue())
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

        self.assertEllipsis("""\
...
    for http://xml.zeit.de/online/2007/01/Flugsicherheit,
        http://xml.zeit.de/online/2007/01/Saarland
Publishing http://xml.zeit.de/online/2007/01/Flugsicherheit,
       http://xml.zeit.de/online/2007/01/Saarland
...
Done http://xml.zeit.de/online/2007/01/Flugsicherheit,
 http://xml.zeit.de/online/2007/01/Saarland (...s)...""",
                            self.log.getvalue())

        self.assertIn('Published', get_object_log(c1))
        self.assertIn('Published', get_object_log(c2))


class PublishErrorEndToEndTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.CELERY_LAYER
    error = "Error during publish/retract: ScriptError: ('', 1)"

    def setUp(self):
        super().setUp()
        self.bak_path = self.layer['publish-script'] + '.bak'
        shutil.move(self.layer['publish-script'], self.bak_path)
        with open(self.layer['publish-script'], 'w') as f:
            f.write('#!/bin/sh\nexit 1')
        os.chmod(self.layer['publish-script'], 0o755)

    def tearDown(self):
        shutil.move(self.bak_path, self.layer['publish-script'])
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

        self.assertEqual(self.error,
                         str(err.exception))
        self.assertIn(
            self.error,
            [zope.i18n.interpolate(m, m.mapping)
             for m in get_object_log(content)])

    def test_error_during_publish_multiple_is_written_to_objectlog(self):
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

        with self.assertRaises(Exception) as err:
            publish.get()
        transaction.begin()

        self.assertEqual(self.error,
                         str(err.exception))
        self.assertIn(
            self.error,
            [zope.i18n.interpolate(m, m.mapping) for m in get_object_log(c1)])
        self.assertIn(
            self.error,
            [zope.i18n.interpolate(m, m.mapping) for m in get_object_log(c2)])


class MultiPublishRetractTest(zeit.workflow.testing.FunctionalTestCase):

    def test_publishes_and_retracts_multiple_objects_in_single_script_call(
            self):
        c1 = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        c2 = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/eta-zapatero')
        IPublishInfo(c1).urgent = True
        IPublishInfo(c2).urgent = True
        with mock.patch(
                'zeit.workflow.publish.PublishTask.call_script') as script:
            IPublish(self.repository).publish_multiple(
                [c1, c2], background=False)
            script.assert_called_with(
                'publish', ['work/online/2007/01/Somalia',
                            'work/online/2007/01/eta-zapatero'])
        self.assertTrue(IPublishInfo(c1).published)
        self.assertTrue(IPublishInfo(c2).published)

        with mock.patch(
                'zeit.workflow.publish.RetractTask.call_script') as script:
            IPublish(self.repository).retract_multiple(
                [c1, c2], background=False)
            script.assert_called_with(
                'retract', ['work/online/2007/01/Somalia',
                            'work/online/2007/01/eta-zapatero'])
        self.assertFalse(IPublishInfo(c1).published)
        self.assertFalse(IPublishInfo(c2).published)

    def test_accepts_uniqueId_as_well_as_ICMSContent(self):
        with mock.patch('zeit.workflow.publish.MultiPublishTask.run') as run:
            IPublish(self.repository).publish_multiple([
                self.repository['testcontent'],
                'http://xml.zeit.de/online/2007/01/Somalia'], background=False)
            ids = run.call_args[0][0]
            self.assertEqual([
                'http://xml.zeit.de/testcontent',
                'http://xml.zeit.de/online/2007/01/Somalia'], ids)

    def test_empty_list_of_objects_does_not_run_publish(self):
        with mock.patch(
                'zeit.workflow.publish.PublishTask.call_script') as script:
            IPublish(self.repository).publish_multiple([], background=False)
            self.assertFalse(script.called)

    def test_error_in_one_item_continues_with_other_items(self):
        c1 = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        c2 = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/eta-zapatero')
        IPublishInfo(c1).urgent = True
        IPublishInfo(c2).urgent = True

        calls = []

        def after_publish(context, event):
            calls.append(context.uniqueId)
            if context.uniqueId == c1.uniqueId:
                raise RuntimeError('provoked')
        zope.component.getGlobalSiteManager().registerHandler(
            after_publish,
            (zeit.cms.interfaces.ICMSContent,
             zeit.cms.workflow.interfaces.IPublishedEvent))

        with self.assertRaises(RuntimeError):
            IPublish(self.repository).publish_multiple(
                [c1, c2], background=False)

        # PublishedEvent still happens for c2, even though c1 raised
        self.assertIn(c2.uniqueId, calls)
        # Error is logged
        log = zeit.objectlog.interfaces.ILog(c1)
        self.assertEqual(
            ['${name}: ${new_value}',
             'Collective Publication of ${count} objects',
             'Error during publish/retract: ${exc}: ${message}'],
            [x.message for x in log.get_log()])


class NewPublisherTest(zeit.workflow.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.LAYER

    @pytest.fixture(autouse=True)
    def monkeypatch(self, monkeypatch):
        self.monkeypatch = monkeypatch

    def test_object_is_published(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            self.assertEqual(
                'http://xml.zeit.de/online/2007/01/Somalia',
                result['uniqueId'])
            self.assertIn('uuid', result)
        self.assertTrue(IPublishInfo(article).published)

    def test_authordashboard_is_notified(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_authordashboard = result['authordashboard']
            result_authordashboard.pop('uuid')  # NOTE changes each run
            self.assertEqual({
                'unique_id': 'http://xml.zeit.de/online/2007/01/Somalia',
            }, result_authordashboard)
        self.assertTrue(IPublishInfo(article).published)

    def test_bigquery_is_published(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_fbnt = result['bigquery']
            result_fbnt.pop('uuid')  # NOTE changes each run
            self.assertEqual({
                'unique_id': 'http://xml.zeit.de/online/2007/01/Somalia',
                'path': '/online/2007/01/Somalia'},
                result_fbnt)
        self.assertTrue(IPublishInfo(article).published)

    def test_bigquery_adapters_are_registered(self):
        import zeit.content.article.article
        import zeit.content.cp.centerpage
        import zeit.content.gallery.gallery
        import zeit.content.video.video
        article = zeit.content.article.article.Article()
        assert zope.component.queryAdapter(
            article, zeit.workflow.interfaces.IPublisherData,
            name="bigquery") is not None
        centerpage = zeit.content.cp.centerpage.CenterPage()
        assert zope.component.queryAdapter(
            centerpage, zeit.workflow.interfaces.IPublisherData,
            name="bigquery") is not None
        gallery = zeit.content.gallery.gallery.Gallery()
        assert zope.component.queryAdapter(
            gallery, zeit.workflow.interfaces.IPublisherData,
            name="bigquery") is not None
        video = zeit.content.video.video.Video()
        assert zope.component.queryAdapter(
            video, zeit.workflow.interfaces.IPublisherData,
            name="bigquery") is not None

    def test_comments_are_published(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_comments = result['comments']
            result_comments.pop('uuid')  # NOTE changes each run
            self.assertEqual({
                'comments_allowed': False,
                'pre_moderated': False,
                'type': 'commentsection',
                'unique_id': 'http://xml.zeit.de/online/2007/01/Somalia',
                'visible': False}, result_comments)
        self.assertTrue(IPublishInfo(article).published)

    def test_comments_adapters_are_registered(self):
        import zeit.content.article.article
        import zeit.content.gallery.gallery
        import zeit.content.video.video
        article = zeit.content.article.article.Article()
        assert zope.component.queryAdapter(
            article, zeit.workflow.interfaces.IPublisherData,
            name="comments") is not None
        gallery = zeit.content.gallery.gallery.Gallery()
        assert zope.component.queryAdapter(
            gallery, zeit.workflow.interfaces.IPublisherData,
            name="comments") is not None
        video = zeit.content.video.video.Video()
        assert zope.component.queryAdapter(
            video, zeit.workflow.interfaces.IPublisherData,
            name="comments") is not None

    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def test_facebooknewstab_is_published(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_fbnt = result['facebooknewstab']
            result_fbnt.pop('uuid')  # NOTE changes each run
            self.assertEqual({
                'unique_id': 'http://xml.zeit.de/online/2007/01/Somalia',
                'path': '/online/2007/01/Somalia'},
                result_fbnt)
        self.assertTrue(IPublishInfo(article).published)

    def test_facebooknewstab_skipped_date_first_released(self):
        FEATURE_TOGGLES.set('new_publisher')
        # this article has date_first_published set to an old date
        article = ICMSContent('http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        IPublishInfo(article).urgent = True
        self.assertTrue(IPublishInfo(article).published)
        self.assertEqual(IPublishInfo(article).date_first_released.year, 2020)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' not in result
        # set it to something else and make sure nothing else caused the skip
        info = IPublishInfo(article)
        info.date_first_released = info.date_first_released.replace(
            year=2022)
        self.assertEqual(IPublishInfo(article).date_first_released.year, 2022)
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' in result

    def test_facebooknewstab_skipped_product_id(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        self.assertFalse(IPublishInfo(article).published)
        self.assertEqual(article.product.id, "ZEDE")
        # we add more products than needed for the test to make sure
        # the config parsing works correctly
        config['facebooknewstab-ignore-products'] = "ADV, VAB, ZEDE"
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' not in result
        # set it to something else and make sure nothing else caused the skip
        with checked_out(article) as co:
            co.product = zeit.cms.content.sources.Product("ZTGS")
        self.assertEqual(article.product.id, "ZTGS")
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' in result

    def test_facebooknewstab_skipped_ressort(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        self.assertFalse(IPublishInfo(article).published)
        self.assertEqual(article.ressort, "International")
        # we add more products than needed for the test to make sure
        # the config parsing works correctly, that is also why there is
        # a space in front of International
        config['facebooknewstab-ignore-ressorts'] = ",".join([
            "Administratives", " International"])
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' not in result
        # set it to something else and make sure nothing else caused the skip
        with checked_out(article) as co:
            co.ressort = "Politik"
        self.assertEqual(article.ressort, "Politik")
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            assert 'facebooknewstab' in result

    def test_speechbert_is_published(self):
        FEATURE_TOGGLES.set('new_publisher')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        IPublishInfo(article).urgent = True
        self.assertFalse(IPublishInfo(article).published)
        assert article.audio_speechbert is None
        with requests_mock.Mocker() as rmock:
            response = rmock.post(
                'http://localhost:8060/test/publish', status_code=200)
            IPublish(article).publish(background=False)
            (result,) = response.last_request.json()
            result_sb = result['speechbert']
            self.assertEqual(
                ['payload', 'unique_id', 'uuid'],
                sorted(result_sb.keys()))
            # TODO: the following assert should fail, we tested above that
            # the attribute is None, but in Speechbert.json() it is True
            # assert 'hasAudio' not in result_sb['payload']
            result_sb = zeit.workflow.publish_3rdparty.Speechbert(
                article).json()
            assert result_sb['payload']['hasAudio'] is True
        self.assertTrue(IPublishInfo(article).published)
        assert article.audio_speechbert is True

    def test_speechbert_ignore_genres(self):
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        # disable the max-age filter
        config['speechbert-max-age'] = sys.maxsize
        config['speechbert-ignore-genres'] = 'rezept-vorstellung'
        data_factory = zeit.workflow.publish_3rdparty.Speechbert(article)
        assert data_factory.json() is None
        config['speechbert-ignore-genres'] = ''
        data_factory = zeit.workflow.publish_3rdparty.Speechbert(article)
        assert data_factory.json() is not None

    def test_speechbert_ignore_templates(self):
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        # disable the max-age filter
        config['speechbert-max-age'] = sys.maxsize
        config['speechbert-ignore-templates'] = 'article'
        data_factory = zeit.workflow.publish_3rdparty.Speechbert(article)
        assert data_factory.json() is None
        config['speechbert-ignore-templates'] = ''
        data_factory = zeit.workflow.publish_3rdparty.Speechbert(article)
        assert data_factory.json() is not None

    def test_speechbert_max_age(self):
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        data_factory = zeit.workflow.publish_3rdparty.Speechbert(article)
        assert data_factory.json() is None
        config['speechbert-max-age'] = sys.maxsize
        data_factory = zeit.workflow.publish_3rdparty.Speechbert(article)
        assert data_factory.json() is not None

    def test_speechbert_extraction(self):
        import json
        import lxml.etree
        import pkg_resources
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        source = pkg_resources.resource_string(
            'zeit.workflow.tests', 'fixtures/speechbert.xslt')
        transform = lxml.etree.XSLT(lxml.etree.XML(source))
        stack = [ICMSContent('http://xml.zeit.de/')]
        while stack:
            resource = stack.pop()
            folder = zeit.cms.repository.interfaces.IFolder(resource, None)
            if folder is not None:
                stack.extend(folder.values())
                continue
            article = zeit.content.article.interfaces.IArticle(resource, None)
            if article is None:
                continue
            doc = resource.xml
            original_transformed = str(transform(doc))
            expected = json.loads(original_transformed)
            data_factory = zeit.workflow.publish_3rdparty.Speechbert(
                resource)
            result = data_factory.json()['payload']
            assert result == expected

    def test_speechbert_payload(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        del payload['body']  # not relevant in this test
        del payload['image']  # not relevant in this test
        assert payload == dict(
            access='abo',
            authors=['Eva Biringer'],
            channels='zeit-magazin essen-trinken',
            genre='rezept-vorstellung',
            headline='Vier Rezepte für eine Herdplatte',
            lastModified='2020-04-14T09:19:59.618155+00:00',
            publishDate='2020-04-14T09:19:59.618155+00:00',
            section='zeit-magazin',
            subsection='essen-trinken',
            subtitle=(
                'Ist genug Brot und Kuchen gebacken, bleibt endlich wieder '
                'Zeit, zu kochen. Mit diesen One-Pot-Gerichten können Sie den '
                'Zuckerschock vom Osterwochenende kontern.'),
            tags=[
                'Kochrezept',
                'Coronavirus',
                'Quarantäne',
                'Social Distancing',
                'Rezept',
                'Mahlzeit',
                'kochen'],
            teaser=(
                'Ist genug Brot und Kuchen gebacken, '
                'bleibt endlich wieder Zeit, zu kochen.'),
            url='',
            uuid='16e82986-cdc0-492d-84e8-267d09b4ab53')

    def test_speechbert_payload_access_free(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        assert article.access == 'free'
        assert 'access' not in payload

    def test_speechbert_payload_no_authors(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/terror-abschuss-schaeuble')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        assert article.authors == ()
        assert payload['authors'] == []

    def test_speechbert_payload_multiple_authors(self):
        # TODO: there is no existing test data with multiple authors
        pass

    def test_speechbert_payload_no_channels(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        assert article.channels == ()
        assert 'channels' not in payload

    def test_speechbert_payload_single_channel(self):
        # TODO: there is no existing test data with a single channel
        pass

    def test_speechbert_payload_no_genre(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        assert article.genre is None
        assert 'genre' not in payload

    def test_speechbert_payload_no_image(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        assert isinstance(
            article.main_image,
            zeit.content.article.article.NoMainImageBlockReference)
        assert 'image' not in payload

    def test_speechbert_payload_no_last_modified(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        info = zeit.cms.workflow.interfaces.IPublishInfo(article)
        assert info.date_last_published_semantic is None
        assert 'lastModified' not in payload

    def test_speechbert_payload_no_publish_date(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        info = zeit.cms.workflow.interfaces.IPublishInfo(article)
        assert info.date_first_released is None
        assert 'publishDate' not in payload

    def test_speechbert_payload_sub_section(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        assert article.sub_ressort is None
        assert 'subsection' not in payload

    def test_speechbert_payload_series(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        assert article.serie is not None
        assert payload['series'] == '-'

    def test_speechbert_payload_supertitle(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        assert article.supertitle == 'Geopolitik'
        assert payload['supertitle'] == 'Geopolitik'

    def test_speechbert_payload_no_uuid(self):
        self.monkeypatch.setattr(
            zeit.workflow.publish_3rdparty.Speechbert,
            'ignore',
            lambda s, d: False)
        article = ICMSContent(
            'http://xml.zeit.de/online/2007/01/weissrussland-russland-gas')
        payload = zeit.workflow.publish_3rdparty.Speechbert(
            article).json()['payload']
        assert zeit.cms.content.interfaces.IUUID(article).shortened is None
        assert 'uuid' not in payload
