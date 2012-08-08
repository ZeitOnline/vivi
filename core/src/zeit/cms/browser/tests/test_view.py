# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2
import zeit.cms.testing


class TestJSON(unittest2.TestCase):

    def test_dict_result_should_pop_template(self):
        from zeit.cms.browser.view import JSON

        class View(JSON):
            def json(self):
                return result
            resources = mock.MagicMock()
            resources.__getitem__().return_value = 'mocked template'
        result = {'template': 'bla'}
        view = View()
        view.request = mock.Mock()
        self.assertEqual('{"template_url": "mocked template"}', view())
        self.assertEqual({'template_url': 'mocked template'}, result)

    def test_non_dict_result_should_not_pop_template(self):
        from zeit.cms.browser.view import JSON

        class View(JSON):
            def json(self):
                return result
        result = [1, 2, 3]
        view = View()
        view.request = mock.Mock()
        self.assertEqual('[1, 2, 3]', view())
        # result is unaltered
        self.assertEqual([1, 2, 3], result)


class FragmentReady(zeit.cms.testing.SeleniumTestCase):

    def setUp(self):
        super(FragmentReady, self).setUp()
        self.open(
            '/@@/zeit.cms.javascript.base/tests/fragmentready.html')

    def test_event_is_fired_on_document_and_contains_actual_dom_element(self):
        self.eval('window.jQuery("#example").trigger_fragment_ready();')
        self.assertEqual('example', self.eval('zeit.cms.event_target'))
