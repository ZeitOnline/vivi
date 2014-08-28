from zeit.cms.testcontenttype.testcontenttype import TestContentType
import lxml.etree
import mock
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

    def tests_values_contain_only_blocks_with_content(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticRegion(lead)
        auto.count = 5
        auto.automatic = True
        self.assertEqual(0, len(auto.values()))

    def test_only_marked_articles_are_put_into_leader_block(self):
        self.repository['normal'] = TestContentType()
        self.repository['leader'] = TestContentType()

        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticRegion(lead)
        auto.count = 2
        auto.automatic = True

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [dict(uniqueId='http://xml.zeit.de/normal'),
                                   dict(uniqueId='http://xml.zeit.de/leader',
                                        lead_candidate=True)]
            result = auto.values()
        self.assertEqual(
            'http://xml.zeit.de/leader', list(result[0])[0].uniqueId)
        self.assertEqual(
            'http://xml.zeit.de/normal', list(result[1])[0].uniqueId)

    def test_renders_xml_with_filled_in_blocks(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticRegion(lead)
        auto.count = 1
        auto.automatic = True

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent',
                     lead_candidate=True)]
            xml = zeit.content.cp.interfaces.IRenderedXML(lead)
        self.assertEllipsis(
            """\
<region...>
  <container...type="teaser"...>
    <block...href="http://xml.zeit.de/testcontent"...""",
            lxml.etree.tostring(xml, pretty_print=True))

    def test_stores_query_in_xml(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticRegion(lead)
        self.assertEqual((), auto.query)
        auto.query = (
            ('Channel', 'International', 'Nahost'),
            ('Channel', 'Wissen', None))
        self.assertEllipsis(
            """<...
            <query>
              <condition...type="Channel"...>International Nahost</condition>
              <condition...type="Channel"...>Wissen</condition>
            </query>...""", lxml.etree.tostring(auto.xml, pretty_print=True))
