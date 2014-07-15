import zeit.content.cp.interfaces
import zeit.content.cp.testing


class AutomaticRegionTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticRegionTest, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()

    def test_fills_with_placeholders_when_set_to_automatic(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticRegion(lead)
        auto.count = 5
        auto.automatic = True
        self.assertEqual(5, len(lead))

    def test_fills_with_placeholders_when_teaser_count_changed(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticRegion(lead)
        auto.count = 5
        auto.automatic = True
        self.assertEqual(5, len(lead))
        auto.count = 7
        self.assertEqual(7, len(lead))
