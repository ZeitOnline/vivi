import zeit.content.image.testing


class TestXMPMetadataView(zeit.content.image.testing.BrowserTestCase):
    def test_smoke_xmp_tab_is_registered(self):
        # We don't yet know if the current formatting is helpful,
        # so don't assert anything about that yet.
        self.browser.open('/repository/image/@@xmp.html')
        self.assertEllipsis('...XMP Metadata...', self.browser.contents)

        self.browser.open('/repository/group/@@xmp.html')
        self.assertEllipsis('...XMP Metadata...', self.browser.contents)
