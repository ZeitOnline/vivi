# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.cp.browser.testing
import zeit.content.cp.testing


class CommonEditTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def test_background_color_is_validated(self):
        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        contents_url = b.url
        b.open(
            'lead/@@landing-zone-drop?uniqueId=http://xml.zeit.de/testcontent&order=top')
        b.open(contents_url)
        b.getLink('Common', index=1).click()
        form_url = b.url

        b.getControl('Background color (ZMO only)').value = 'xyz'
        b.getControl('Apply').click()
        self.assertEllipsis('...Invalid hex literal...', b.contents)
        b.getControl('Background color (ZMO only)').value = 'ffffff'
        b.getControl('Apply').click()
        b.open(form_url)
        self.assertEqual(
            'ffffff', b.getControl('Background color (ZMO only)').value)
