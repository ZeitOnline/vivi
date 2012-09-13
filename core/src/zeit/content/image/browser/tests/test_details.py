# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.image.tests


class ImageDetails(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.content.image.tests.selenium_layer

    def test_clicking_button_shows_details_pane(self):
        s = self.selenium
        self.open('/repository/2006/DSC00109_2.JPG/@@wrap?view=object-details')
        s.assertNotVisible('css=.picture_information')
        self.eval('window.jQuery(document).trigger_fragment_ready();')
        s.click('css=.toggle_infos')
        s.waitForVisible('css=.picture_information')
