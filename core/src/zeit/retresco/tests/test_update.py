from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import StringIO
import gocept.async
import gocept.async.tests
import logging
import mock
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
import mechanize


@gocept.async.function(service='events')
def checkout_and_checkin():
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    with zeit.cms.checkout.helper.checked_out(repository['testcontent']):
        pass


def process():
    log_output = StringIO.StringIO()
    log_handler = logging.StreamHandler(log_output)
    logging.root.addHandler(log_handler)
    old_log_level = logging.root.level
    logging.root.setLevel(logging.ERROR)
    try:
        gocept.async.tests.process()
    finally:
        logging.root.removeHandler(log_handler)
        logging.root.setLevel(old_log_level)
    assert not log_output.getvalue(), log_output.getvalue()


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
        process()
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
        try:
            process()
        except IndexError:
            pass
        self.assertFalse(self.tms.index.called)

    def test_checkin_should_index(self):
        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content):
            pass
        process()
        self.tms.enrich.assert_called_with(content)
        self.tms.index.assert_called_with(content)

    def test_index_should_be_called_from_async(self):
        checkout_and_checkin()
        self.assertFalse(self.tms.index.called)
        process()
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
                process()
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
        process()
        self.tms.delete_id.assert_called_with(uuid)

    def test_remove_from_workingcopy_does_nothing(self):
        content = ExampleContentType()
        event = zope.lifecycleevent.ObjectRemovedEvent(content)
        event.oldParent = zeit.cms.workingcopy.workingcopy.Workingcopy()
        zope.event.notify(event)
        try:
            process()
        except IndexError:
            pass
        self.assertFalse(self.tms.delete.called)

    def test_publish_should_index_with_published_true(self):
        # Right now this works without us having to anything special, since at
        # BeforePublishEvent time, zeit.workflow first sets published=True
        # and related properties, and then triggers a checkout/checkin cycle
        # -- which on checkin triggers the indexing.
        def index(tms, content):
            self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(
                content).published)
        self.tms.index = index
        content = self.repository['testcontent']
        zeit.cms.workflow.interfaces.IPublishInfo(content).urgent = True
        zeit.cms.workflow.interfaces.IPublish(content).publish()
        zeit.workflow.testing.run_publish()


class TMSUpdateRequestTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.retresco.testing.ZCML_LAYER

    def test_endpoint_avoids_get(self):
        b = zope.testbrowser.testing.Browser()
        with self.assertRaisesRegexp(mechanize.HTTPError,
                                     'HTTP Error 400: Bad Request'):
            b.open('http://localhost/@@update_keywords_by_list')

    def test_endpoint_rejects_post_without_doc_ids(self):
        b = zope.testbrowser.testing.Browser()
        with self.assertRaisesRegexp(mechanize.HTTPError,
                                     'HTTP Error 400: Bad Request'):
            b.post('http://localhost/@@update_keywords_by_list', '')
        with self.assertRaisesRegexp(mechanize.HTTPError,
                                     'HTTP Error 400: Bad Request'):
            b.post('http://localhost/@@update_keywords_by_list',
                   '{"foo" : "bar"}', 'application/x-javascript')

    def test_endpoint_rejects_invalid_doc_ids(self):
        b = zope.testbrowser.testing.Browser()
        with self.assertRaisesRegexp(mechanize.HTTPError,
                                     'HTTP Error 422: Unprocessable Entity'):
            b.post('http://localhost/@@update_keywords_by_list',
                   '{"doc_ids" : [1, 2, 3]}', 'application/x-javascript')

    def test_endpoint_successful_update_vaild_article(self):
        b = zope.testbrowser.testing.Browser()
        b.post('http://localhost/@@update_keywords_by_list',
               '{"doc_ids" : ['
                '"{urn:uuid:9cb93717-2467-4af5-9521-25110e1a7ed8}", '
                '"{urn:uuid:0da8cb59-1a72-4ae2-bbe2-006e6b1ff621}"]}',
                'application/x-javascript')
        self.assertEquals('{"update": true}', b.contents)
        self.assertEquals('200 Ok', b.headers.getheader('status'))
