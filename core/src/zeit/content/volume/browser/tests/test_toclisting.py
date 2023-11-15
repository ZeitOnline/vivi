import zeit.content.volume.testing


class TocListingTest(zeit.content.volume.testing.BrowserTestCase):
    def test_toclisting_tab_is_available(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/')

        self.assertEqual('<li class="table_of_content ">' in b.contents, True)

    def test_toclisting_filter_is_available(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/@@toc-listing.html')

        self.assertEqual('<div id="tocListingFilter">' in b.contents, True)

    def test_toclisting_columns_are_available(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/@@toc-listing.html')

        self.assertEllipsis('...<span...Supertitle...</span>...', b.contents)
        self.assertEllipsis('...<span...Ressort...</span>...', b.contents)
        self.assertEllipsis('...<span...Urgent...</span>...', b.contents)
        self.assertEllipsis('...<span...status-seo-optimized...</span>...', b.contents)
        self.assertEllipsis('...<span...Teaserimage...</span>...', b.contents)
