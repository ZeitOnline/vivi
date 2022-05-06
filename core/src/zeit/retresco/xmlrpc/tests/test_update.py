# coding: utf-8
from io import StringIO
from unittest import mock
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import logging
import zeit.cms.interfaces
import zeit.cms.webtest
import zeit.retresco.testing
import zope.component


class XMLRPCTest(zeit.retresco.testing.BrowserTestCase):

    def setUp(self):
        super().setUp()
        server = zeit.cms.webtest.ServerProxy(
            'http://index:indexpw@localhost/', self.layer['wsgi_app'])
        self.update = getattr(server, '@@update_tms')

        self.tms = mock.Mock()
        self.tms.get_article_data.return_value = {}
        self.tms.enrich.return_value = {}
        self.tms.generate_keyword_list.return_value = []
        zope.component.getGlobalSiteManager().registerUtility(
            self.tms, zeit.retresco.interfaces.ITMS)

        self.log = StringIO()
        self.log_handler = logging.StreamHandler(self.log)
        logging.root.addHandler(self.log_handler)
        self.old_log_level = logging.root.level
        logging.root.setLevel(logging.INFO)

    def tearDown(self):
        logging.root.removeHandler(self.log_handler)
        logging.root.setLevel(self.old_log_level)
        super().tearDown()

    def test_xmlrpc_update_should_call_index(self):
        id = 'http://xml.zeit.de/online/2007/01/Somalia'
        self.update(id)
        self.tms.index.assert_called_with(
            zeit.cms.interfaces.ICMSContent(id), {'body': None})
        self.tms.enrich.assert_called_with(zeit.cms.interfaces.ICMSContent(id))
        self.assertIn(
            "zope.index triggered TMS index update for "
            "'http://xml.zeit.de/online/2007/01/Somalia'", self.log.getvalue())

    def test_nonexistent_id_should_be_ignored(self):
        self.update('http://xml.zeit.de/nonexistent')
        self.assertFalse(self.tms.index.called)
        self.assertIn(
            'http://xml.zeit.de/nonexistent does not exist anymore',
            self.log.getvalue())

    def test_non_ascii_id_should_work(self):
        self.repository['föö'] = ExampleContentType()
        id = 'http://xml.zeit.de/föö'
        self.update(id)
        self.tms.index.assert_called_with(
            zeit.cms.interfaces.ICMSContent(id), {'body': None})
