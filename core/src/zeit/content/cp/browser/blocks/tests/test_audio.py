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
    def test_podcastmetadata_can_be_added(self):
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage.body['lead'].create_item('podcastmetadata')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.assertEqual(1, b.contents.count('type-podcastmetadata'))
