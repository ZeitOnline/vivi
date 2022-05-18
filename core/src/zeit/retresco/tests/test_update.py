from unittest import mock
from zeit.cms.tagging.tag import Tag
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.retresco.interfaces import TechnicalError
import transaction
import zeit.cms.checkout.helper
import zeit.cms.workflow.interfaces
import zeit.cms.workingcopy.workingcopy
import zeit.retresco.testing
import zeit.retresco.update
import zeit.workflow.interfaces
import zope.component
import zope.event
import zope.lifecycleevent


class UpdateTest(zeit.retresco.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.tms = mock.Mock()
        self.tms.get_article_data.return_value = {}
        self.tms.enrich.return_value = {}
        self.tms.generate_keyword_list.return_value = []
        zope.component.getGlobalSiteManager().registerUtility(
            self.tms, zeit.retresco.interfaces.ITMS)

    def test_creating_content_should_index(self):
        self.repository['t1'] = ExampleContentType()
        self.tms.enrich.assert_called_with(self.repository['t1'])
        self.tms.index.assert_called_with(
            self.repository['t1'], {'body': None})

    def test_event_dispatched_to_sublocation_should_be_ignored(self):
        # XXX: I'm not quite sure which use cases actually create this kind of
        # ObjectAddedEvent, but we've inherited this guard from zeit.solr and
        # they probably had a good reason. %-)
        content = ExampleContentType()
        content.uniqueId = 'xzy://bla/fasel'
        content_sub = ExampleContentType()
        content_sub.uniqueId = 'xzy://bla/fasel/sub'
        event = zope.lifecycleevent.ObjectAddedEvent(content)
        for ignored in zope.component.subscribers((content_sub, event), None):
            pass
        self.assertFalse(self.tms.index.called)

    def test_checkin_should_index(self):
        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content):
            pass
        self.tms.enrich.assert_called_with(content)
        self.tms.index.assert_called_with(content, {'body': None})

    def test_checkin_should_update_keywords_if_none_exist(self):
        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content):
            pass
        self.assertEqual(True, self.tms.generate_keyword_list.called)

    def test_checkin_should_not_update_keywords_if_already_present(self):
        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.keywords = (Tag('Berlin', 'location'),)
        self.assertEqual(False, self.tms.generate_keyword_list.called)

    def test_checkin_should_index_asynchronously(self):
        content = self.repository['testcontent']
        with mock.patch('zeit.retresco.update.index_async') as index:
            with zeit.cms.checkout.helper.checked_out(content):
                pass
            self.assertTrue(index.apply_async.called)

    def test_checkin_should_enrich_marked_content(self):
        content = ExampleContentType()
        zope.interface.alsoProvides(
            content, zeit.retresco.interfaces.ISkipEnrich)
        self.repository['t1'] = content
        with zeit.cms.checkout.helper.checked_out(self.repository['t1']):
            pass
        self.assertFalse(self.tms.enrich.called)

    def test_folders_should_be_indexed_recursively(self):
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2007/01')
        zeit.retresco.update.index(folder)
        # 1 Folder + 40 objects contained in it
        self.assertEqual(41, self.tms.index.call_count)

    def test_non_recursive_folders_should_not_be_indexed_recursively(self):
        folder = zeit.cms.repository.folder.Folder()
        zope.interface.alsoProvides(
            folder, zeit.cms.repository.interfaces.INonRecursiveCollection)
        self.repository['nonrecursive'] = folder
        self.repository['nonrecursive']['test'] = ExampleContentType()

        self.tms.index.reset_mock()
        zeit.retresco.update.index(folder)
        self.assertEqual(1, self.tms.index.call_count)

    def test_index_async_should_not_raise_when_object_vanished(self):
        with mock.patch('zeit.cms.interfaces.ICMSContent') as cmscontent:
            with mock.patch('zeit.retresco.update.index') as index:
                cmscontent.return_value = None
                zeit.retresco.update.index_async(
                    'http://xml.zeit.de/testcontent')
                self.assertFalse(index.called)

    def test_publish_should_not_be_called_on_index_if_res_not_published(self):
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pub:
            content = self.repository['testcontent']
            pub_info = mock.Mock()
            pub_info.published = False
            pub.return_value = pub_info
            zeit.retresco.update.index(content, enrich=False, publish=True)
            self.assertFalse(self.tms.publish.called)

    def test_publish_should_be_called_on_index_if_res_published(self):
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pub:
            with mock.patch(
                    'zeit.retresco.interfaces.ITMSRepresentation') as tmsrep:
                tmsrep().return_value = {'not empty': ''}
                content = self.repository['testcontent']
                pub_info = mock.Mock()
                pub_info.published = True
                pub.return_value = pub_info
                zeit.retresco.update.index(content, enrich=False, publish=True)
                self.assertTrue(self.tms.publish.called)

    def test_publish_should_not_be_called_on_index_without_option(self):
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pub:
            content = self.repository['testcontent']
            pub_info = mock.Mock()
            pub_info.published = True
            pub.return_value = pub_info
            zeit.retresco.update.index(content)
            self.assertFalse(self.tms.publish.called)

    def test_should_pass_body_from_enrich_to_index(self):
        content = self.repository['testcontent']
        self.tms.enrich.return_value = {'body': 'mybody'}
        zeit.retresco.update.index(content, enrich=True)
        self.tms.index.assert_called_with(content, {'body': 'mybody'})

    def test_index_should_preserve_kpi_fields(self):
        content = self.repository['testcontent']
        self.tms.get_article_data.return_value = {'kpi_1': 'kpi1'}
        zeit.retresco.update.index(content)
        self.tms.index.assert_called_with(content, {'kpi_1': 'kpi1'})

    def test_removed_event_should_unindex(self):
        content = self.repository['testcontent']
        uuid = zeit.cms.content.interfaces.IUUID(content).id
        zope.event.notify(zope.lifecycleevent.ObjectRemovedEvent(content))
        self.tms.delete_id.assert_called_with(uuid)
        self.assertFalse(self.tms.index.called)

    def test_remove_from_workingcopy_does_nothing(self):
        content = ExampleContentType()
        event = zope.lifecycleevent.ObjectRemovedEvent(content)
        event.oldParent = zeit.cms.workingcopy.workingcopy.Workingcopy()
        zope.event.notify(event)
        self.assertFalse(self.tms.delete.called)

    def test_rename_should_index(self):
        zope.copypastemove.interfaces.IObjectMover(
            self.repository['testcontent']).moveTo(self.repository, 'changed')
        self.assertTrue(self.tms.index.called)

    def test_changing_workflow_properties_in_repository_should_index(self):
        content = self.repository['testcontent']
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        event = zeit.cms.content.interfaces.DAVPropertyChangedEvent(
            workflow, 'ns', 'name', 'old', 'new',
            zeit.workflow.interfaces.IContentWorkflow['urgent'])

        zope.interface.alsoProvides(
            content, zeit.cms.checkout.interfaces.ILocalContent)
        zope.event.notify(event)
        self.assertFalse(self.tms.index.called)

        zope.interface.noLongerProvides(
            content, zeit.cms.checkout.interfaces.ILocalContent)
        zope.event.notify(event)
        self.assertTrue(self.tms.index.called)


class UpdatePublishTest(zeit.retresco.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.tms = mock.Mock()
        self.tms.get_article_data.return_value = {}
        zope.component.getGlobalSiteManager().registerUtility(
            self.tms, zeit.retresco.interfaces.ITMS)

    def test_publish_should_index_with_published_true(self):
        published = []

        def index(content, overrides=None):
            published.append(zeit.cms.workflow.interfaces.IPublishInfo(
                content).published)
        self.tms.index = index
        content = self.repository['testcontent']
        zeit.cms.workflow.interfaces.IPublishInfo(content).urgent = True
        zeit.cms.workflow.interfaces.IPublish(content).publish(
            background=False)
        # 2 calls: set urgent, then publish
        self.assertEqual([False, True], published)

        content = self.repository['2006']['DSC00109_2.JPG']
        zeit.cms.workflow.interfaces.IPublishInfo(content).urgent = True
        zeit.cms.workflow.interfaces.IPublish(content).publish(
            background=False)
        self.assertEqual([False, True, True], published)

    def test_retract_should_index_with_published_false(self):
        published = []

        def index(content, overrides=None):
            published.append(zeit.cms.workflow.interfaces.IPublishInfo(
                content).published)
        self.tms.index = index
        content = self.repository['testcontent']
        zeit.cms.workflow.interfaces.IPublishInfo(content).published = True
        zeit.cms.workflow.interfaces.IPublish(content).retract(
            background=False)
        self.assertEqual([False], published)

        content = self.repository['2006']['DSC00109_2.JPG']
        zeit.cms.workflow.interfaces.IPublishInfo(content).published = True
        zeit.cms.workflow.interfaces.IPublish(content).retract(
            background=False)
        self.assertEqual([False, False], published)


class IndexParallelTest(zeit.retresco.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.index_patch = mock.patch('zeit.retresco.update.index')
        self.index = self.index_patch.start()

    def tearDown(self):
        self.index_patch.stop()
        super().tearDown()

    def test_should_create_job_per_folder_entry(self):
        zeit.retresco.update.index_parallel.delay(
            'http://xml.zeit.de/online/2007/')
        self.assertEqual(54, self.index.call_count)

    def test_should_not_recurse_into_nonrecursive_collections(self):
        folder = zeit.cms.repository.folder.Folder()
        zope.interface.alsoProvides(
            folder, zeit.cms.repository.interfaces.INonRecursiveCollection)
        self.repository['nonrecursive'] = folder
        self.repository['nonrecursive']['test'] = ExampleContentType()
        self.index.reset_mock()
        zeit.retresco.update.index_parallel.delay(
            'http://xml.zeit.de/nonrecursive/')
        self.assertEqual(1, self.index.call_count)

    def test_should_pass_parameters_through_recursion(self):
        self.repository['testing']['foo'] = ExampleContentType()
        zeit.retresco.update.index_parallel.delay(
            'http://xml.zeit.de/testing/',
            enrich=True, publish=True)
        self.assertEqual(
            dict(enrich=True, update_keywords=True, publish=True),
            self.index.call_args[1])


class RetryTest(zeit.retresco.testing.FunctionalTestCase):

    layer = zeit.retresco.testing.CELERY_LAYER

    def setUp(self):
        super().setUp()

        self.tms = mock.Mock()
        self.tms.get_article_data.return_value = {}
        self.tms.enrich.return_value = {}
        zope.component.getGlobalSiteManager().registerUtility(
            self.tms, zeit.retresco.interfaces.ITMS)

        self.retry_patch = mock.patch(
            'zeit.cms.celery.Task.default_retry_delay', new=None)
        self.retry_patch.start()

    def tearDown(self):
        self.retry_patch.stop()
        super().tearDown()

    def test_retries_on_technical_error(self):
        self.tms.enrich.side_effect = [TechnicalError('internal', 500), None]
        result = zeit.retresco.update.index_async.delay(
            'http://xml.zeit.de/testcontent')
        transaction.commit()
        result.get()
        self.assertEqual(2, self.tms.enrich.call_count)

    def test_no_retry_on_other_errors(self):
        self.tms.enrich.side_effect = RuntimeError('provoked')
        result = zeit.retresco.update.index_async.delay(
            'http://xml.zeit.de/testcontent')
        transaction.commit()
        result.get()
        self.assertEqual(1, self.tms.enrich.call_count)
