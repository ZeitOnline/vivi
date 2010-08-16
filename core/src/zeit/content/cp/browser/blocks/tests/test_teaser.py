# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest

class TestTeaserDisplay(unittest.TestCase):

    def setUp(self):
        from zeit.content.cp.browser.blocks.teaser import Display
        display = Display()
        display.context = mock.Mock()
        display.request = mock.Mock()
        display.layout = mock.Mock()
        display.url = mock.Mock()
        self.display = display
        self.content = mock.Mock()

    def test_get_image_should_use_preview_when_no_iimages(self):
        with mock.patch('zope.component.queryMultiAdapter') as qma:
            image = self.display.get_image(self.content)
            qma.assert_called_with((self.content, self.display.request),
                                   name='preview')
            self.display.url.assert_called_with(self.content, '@@preview')
            self.assertEqual(image, self.display.url())

    def test_get_image_should_not_break_with_no_iimages_and_no_preview(self):
        self.assertTrue(self.display.get_image(self.content) is None)
