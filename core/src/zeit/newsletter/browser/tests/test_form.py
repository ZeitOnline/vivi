# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.newsletter.testing


class MetadataTest(zeit.newsletter.testing.SeleniumTestCase):

    def test_form_should_save_entered_data_on_blur(self):
        s = self.selenium
        self.open('/repository/newsletter/@@checkout')
        s.waitForElementPresent('id=metadata.subject')
        s.assertValue('id=metadata.subject', '')
        s.type('id=metadata.subject', 'flubber')
        s.fireEvent('id=metadata.subject', 'blur')
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent('id=metadata.subject')
        s.assertValue('id=metadata.subject', 'flubber')
