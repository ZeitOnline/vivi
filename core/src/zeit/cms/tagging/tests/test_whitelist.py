# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import absolute_import
import mock
import pkg_resources
import unittest2 as unittest
import zeit.cms.testing
import zope.testing.cleanup


class TestWhitelist(unittest.TestCase,
                    zope.testing.cleanup.CleanUp):

    def whitelist(self):
        from ..whitelist import Whitelist
        return Whitelist()

    def test_get_url_should_use_cms_product_config(self):
        wl = self.whitelist()
        with mock.patch(
             'zope.app.appsetup.product.getProductConfiguration') as gpc:
            wl._get_url()
        gpc.assert_called_with('zeit.cms')

    def test_fetch_should_load_url_from_get_url(self):
        wl = self.whitelist()
        wl._get_url = mock.Mock(return_value=mock.sentinel.url)
        with mock.patch('urllib2.urlopen') as urlopen:
            wl._fetch()
        urlopen.assert_called_with(mock.sentinel.url)

    def test_fetch_should_return_urlopen_result(self):
        wl = self.whitelist()
        wl._get_url = mock.Mock(return_value=mock.sentinel.url)
        with mock.patch('urllib2.urlopen') as urlopen:
            urlopen.return_value = mock.sentinel.response
            self.assertEqual(mock.sentinel.response, wl._fetch())

    def test_load_should_xml_parse_fetch_result(self):
        wl = self.whitelist()
        wl._fetch = mock.Mock(return_value=mock.sentinel.response)
        with mock.patch('gocept.lxml.objectify.fromfile') as fromfile:
            fromfile().iterchildren.return_value = []
            wl._load()
        fromfile.assert_called_with(mock.sentinel.response)

    def test_load_should_iterate_tag_nodes(self):
        wl = self.whitelist()
        wl._fetch = mock.Mock(return_value=mock.sentinel.response)
        with mock.patch('gocept.lxml.objectify.fromfile') as fromfile:
            fromfile().iterchildren.return_value = []
            wl._load()
        fromfile().iterchildren.assert_called_with('tag')

    def test_load_should_create_tag_for_tag_nodes(self):
        wl = self.whitelist()
        wl._fetch = lambda: pkg_resources.resource_stream(
            __name__, 'whitelist.xml')
        with mock.patch('zeit.cms.tagging.tag.Tag') as Tag:
            wl._load()
        self.assertEqual(52, Tag.call_count)
        Tag.assert_called_with(
            'ae11024e-69e0-4434-b7d3-f66efddb0459', u'Polarkreis'),

    def test_load_should_add_tags_to_whitelist(self):
        wl = self.whitelist()
        wl._fetch = lambda: pkg_resources.resource_stream(
            __name__, 'whitelist.xml')
        wl._load()
        self.assertEqual(52, len(wl))

    def test_accessing_data_attribute_should_trigger_load(self):
        wl = self.whitelist()
        wl._load = mock.Mock(return_value={})
        wl.get(mock.sentinel.code)
        self.assertTrue(wl._load.called)

    def test_load_result_should_be_cached(self):
        wl = self.whitelist()
        wl._fetch = mock.Mock()
        with mock.patch('gocept.lxml.objectify.fromfile') as fromfile:
            fromfile().iterchildren.return_value = []
            fromfile.reset_mock()
            wl._load()
            wl._load()
        self.assertEqual(1, fromfile.call_count)
