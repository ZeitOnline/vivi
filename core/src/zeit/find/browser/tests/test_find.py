# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest


class TestSearchResult(unittest.TestCase):

    def setUp(self):
        from zeit.find.browser.find import SearchResult
        self.search = SearchResult(mock.sentinel.context, mock.sentinel.request)
        self.result = dict(uniqueId=mock.sentinel.uniqueId)

    def test_get_range_today_should_adapt_unique_id(self):
        with mock.patch('zeit.cms.content.interfaces.IAccessCounter') as ac:
            ac().hits = 5
            hits = self.search.get_range_today(self.result)
            self.assertEqual('5', hits)
            ac.assert_called_with(mock.sentinel.uniqueId, None)
            ac().hits = None
            hits = self.search.get_range_today(self.result)
            self.assertEqual('0', hits)

    def test_get_range_today_should_return_0_when_there_is_no_ac(self):
        self.assertEqual('0', self.search.get_range_today(self.result))

    def test_get_range_total_should_add_solr_and_today(self):
        self.result['range'] = 10
        with mock.patch('zeit.cms.content.interfaces.IAccessCounter') as ac:
            ac().hits = 5
            hits = self.search.get_range_total(self.result)
            self.assertEqual('15', hits)

    def test_get_range_total_should_not_fail_for_on_today_hits(self):
        self.result['range'] = 10
        with mock.patch('zeit.cms.content.interfaces.IAccessCounter') as ac:
            ac().hits = None
            hits = self.search.get_range_total(self.result)
            self.assertEqual('10', hits)
