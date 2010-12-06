# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2


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
        self.assertEqual([1,2,3], result)
