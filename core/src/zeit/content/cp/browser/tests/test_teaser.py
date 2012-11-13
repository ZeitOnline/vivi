# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.cp.browser.testing
import zeit.content.cp.testing


class TeaserEditForm(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def test_teaser_supertitle_is_stored_on_free_teaser(self):
        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        contents_url = b.url
        b.open(
            'lead/@@landing-zone-drop?uniqueId=http://xml.zeit.de/testcontent')
        b.open(contents_url)
        b.getLink('Edit teaser list').click()

        b.getLink('Edit').click()
        lightbox_url = b.url

        b.getControl('Teaser kicker').value = 'foo'
        b.getControl('Apply only for this page').click()
        b.open(lightbox_url)
        self.assertEqual('foo', b.getControl('Teaser kicker').value)
