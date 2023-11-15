from unittest import mock
import unittest
import zeit.cms.testing


class TestJSON(unittest.TestCase):
    def test_dict_result_should_pop_template(self):
        from zeit.cms.browser.view import JSON

        class View(JSON):
            def json(self):
                return result

            resource_url = mock.Mock()
            resource_url.return_value = 'mocked template'

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
    layer = zeit.cms.testing.WEBDRIVER_LAYER

    def setUp(self):
        super().setUp()
        self.open('/@@/zeit.cms.browser.tests.fixtures/fragmentready.html')

    def test_event_is_fired_on_document_and_contains_actual_dom_element(self):
        self.execute('window.jQuery("#example").trigger_fragment_ready();')
        self.assertEqual('example', self.eval('zeit.cms.event_target'))
