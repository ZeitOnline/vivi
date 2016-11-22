from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import mock
import transaction
import zeit.cms.checkout.helper
import zeit.cms.repository
import zeit.cms.workflow.interfaces
import zeit.cms.workingcopy.workingcopy
import zeit.retresco.testing
import zeit.retresco.update
import zeit.workflow.testing
import zope.component
import zope.event
import zope.lifecycleevent
import zope.security.management


def checkout_and_checkin():
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    with zeit.cms.checkout.helper.checked_out(repository['testcontent']):
        pass


class UpdateTest(zeit.retresco.testing.FunctionalTestCase):

    def setUp(self):
        super(UpdateTest, self).setUp()
        self.tms = mock.Mock()
        self.tms.enrich.return_value = {}
        self.tms.generate_keyword_list.return_value = []
        self.zca.patch_utility(self.tms, zeit.retresco.interfaces.ITMS)

    def test_creating_content_should_index(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['t1'] = ExampleContentType()
        transaction.commit()
        self.tms.enrich.assert_called_with(repository['t1'])
        self.tms.index.assert_called_with(repository['t1'])

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
        transaction.commit()
        self.assertFalse(self.tms.index.called)

    def test_checkin_should_index(self):
        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content):
            pass
        self.tms.enrich.assert_called_with(content)
        self.tms.index.assert_called_with(content)

    def test_index_should_be_called_from_async(self):
        run_instantly = 'zeit.cms.celery.TransactionAwareTask.run_instantly'
        run_asynchronously = (
            'zeit.cms.celery.TransactionAwareTask.run_asynchronously')
        with mock.patch(run_instantly, return_value=False), \
                mock.patch(run_asynchronously, return_value=False):
            checkout_and_checkin()
            self.assertFalse(self.tms.index.called)

            zope.security.management.endInteraction()
            transaction.commit()
            self.assertTrue(self.tms.index.called)

    def test_folders_should_be_indexed_recursively(self):
        folder = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2007/01')
        zeit.retresco.update.index(folder)
        self.assertTrue(self.tms.index.called)
        # 1 Folder + 40 objects contained in it
        self.assertEquals(41, len(self.tms.index.call_args_list))

    def test_index_async_should_not_raise_when_object_vanished(self):
        with mock.patch('zeit.cms.interfaces.ICMSContent') as cmscontent:
            with mock.patch('zeit.retresco.update.index') as index:
                cmscontent.return_value = None
                zeit.retresco.update.index_async(
                    'http://xml.zeit.de/testcontent')
                transaction.commit()
                self.assertFalse(index.called)

    def test_publish_should_not_be_called_on_index_if_res_not_published(self):
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pub:
            content = self.repository['testcontent']
            pub_info = mock.Mock()
            pub_info.published = False
            pub.return_value = pub_info
            zeit.retresco.update.index(content, False, True)
            self.assertFalse(self.tms.publish.called)

    def test_publish_should_be_called_on_index_if_res_published(self):
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pub:
            content = self.repository['testcontent']
            pub_info = mock.Mock()
            pub_info.published = True
            pub.return_value = pub_info
            zeit.retresco.update.index(content, False, True)
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
        self.tms.index.assert_called_with(content, 'mybody')

    def test_removed_event_should_unindex(self):
        content = self.repository['testcontent']
        uuid = zeit.cms.content.interfaces.IUUID(content).id
        zope.event.notify(zope.lifecycleevent.ObjectRemovedEvent(content))
        transaction.commit()
        self.tms.delete_id.assert_called_with(uuid)

    def test_remove_from_workingcopy_does_nothing(self):
        content = ExampleContentType()
        event = zope.lifecycleevent.ObjectRemovedEvent(content)
        event.oldParent = zeit.cms.workingcopy.workingcopy.Workingcopy()
        zope.event.notify(event)
        transaction.commit()
        self.assertFalse(self.tms.delete.called)

    def test_publish_should_index_with_published_true(self):
        # Right now this works without us having to anything special, since at
        # BeforePublishEvent time, zeit.workflow first sets published=True
        # and related properties, and then triggers a checkout/checkin cycle
        # -- which on checkin triggers the indexing.
        def index(content):
            self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(
                content).published)
        self.tms.index = index
        content = self.repository['testcontent']
        zeit.cms.workflow.interfaces.IPublishInfo(content).urgent = True
        zeit.cms.workflow.interfaces.IPublish(content).publish()
        zeit.workflow.testing.run_publish()
