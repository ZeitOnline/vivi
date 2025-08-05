import zeit.content.cp
import zeit.content.cp.centerpage


class TestPodcastHeader(zeit.content.cp.testing.BrowserTestCase):
    def test_podcastheader_can_be_added(self):
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage.body['lead'].create_item('podcastheader')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.assertEqual(1, b.contents.count('type-podcastheader'))


class TestPodcastMetadata(zeit.content.cp.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage.body['lead'].create_item('podcastmetadata')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_podcastmetadata_can_be_added(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-podcastmetadata'))

    def test_description_is_edited_and_stored(self):
        b = self.browser

        # Edit the description
        b.getLink('Edit block properties', index=0).click()
        description_text = 'This is a test podcast description with some details.'
        b.getControl('Podcast description').value = description_text
        b.getControl('Apply').click()

        # Verify the description was saved by checking the form again
        b.open(self.content_url)
        b.getLink('Edit block properties', index=0).click()
        self.assertEqual(description_text, b.getControl('Podcast description').value.strip())
