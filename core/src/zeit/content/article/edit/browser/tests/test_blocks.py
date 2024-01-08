import sys
import unittest

import zeit.content.article.edit.browser.testing


class DivisionBlockTest(zeit.content.article.edit.browser.testing.EditorTestCase):
    @unittest.skipIf(
        sys.platform == 'darwin', '*testing* focus does not work under OSX for reasons unknown'
    )
    def test_division_is_focused_after_add(self):
        s = self.selenium
        self.add_article()
        block_id = self.create_block('division')
        s.waitForElementPresent('css=#' + block_id + ' textarea:focus')
