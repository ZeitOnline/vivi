# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.testing


class Preview(zeit.content.article.testing.SeleniumTestCase):

    def test_selected_tab_is_stored_across_reload(self):
        self.open('/repository/online/2007/01/Somalia')
        s = self.selenium
        selected_tab = 'css=#preview-tabs .ui-tabs-active'
        s.waitForElementPresent(selected_tab)
        s.waitForText(selected_tab, 'iPad')
        s.click('css=#preview-tabs a:contains("Desktop")')
        s.waitForText(selected_tab, 'Desktop')

        s.refresh()
        s.waitForElementPresent(selected_tab)
        s.waitForText(selected_tab, 'Desktop')
