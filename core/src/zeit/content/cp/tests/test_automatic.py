from zeit.cms.testcontenttype.testcontenttype import TestContentType
import lxml.etree
import mock
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zeit.edit.interfaces
import zope.component
import zope.interface.verify


class AutomaticAreaTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticAreaTest, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()

    def test_fills_with_placeholders_when_set_to_automatic(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 5
        auto.automatic = True
        self.assertEqual(5, len(lead))

    def test_fills_with_placeholders_when_teaser_count_changed(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 5
        auto.automatic = True
        self.assertEqual(5, len(lead))
        auto.count = 7
        self.assertEqual(7, len(lead))

    def tests_values_contain_only_blocks_with_content(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 5
        auto.automatic = True
        with mock.patch('zeit.find.search.search') as search:
            search.return_value = []
            self.assertEqual(0, len(auto.values()))

    def test_only_marked_articles_are_put_into_leader_block(self):
        self.repository['normal'] = TestContentType()
        self.repository['leader'] = TestContentType()

        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
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

    def test_no_marked_articles_available_leader_block_gets_normal_article(
            self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.automatic = True

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent')]
            result = auto.values()
        leader = result[0]
        self.assertEqual(
            'http://xml.zeit.de/testcontent', list(leader)[0].uniqueId)

    def test_no_marked_articles_leader_block_layout_is_changed_virtually(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.automatic = True

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent')]
            result = auto.values()
        leader = result[0]
        self.assertEqual('buttons', leader.layout.id)
        self.assertEqual('leader', lead.values()[0].layout.id)
        self.assertEllipsis('...module="buttons"...', lxml.etree.tostring(
            zeit.content.cp.interfaces.IRenderedXML(leader),
            pretty_print=True))

    def test_renders_xml_with_filled_in_blocks(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticRegion(lead)
        auto.count = 1
        auto.automatic = True

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent')]
            result = auto.values()
        leader = result[0]
        self.assertEqual('buttons', leader.layout.id)
        self.assertEqual('leader', lead.values()[0].layout.id)

    def test_renders_xml_with_filled_in_blocks(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
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

    def test_cms_content_iter_returns_filled_in_blocks(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.automatic = True

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent',
                     lead_candidate=True)]
            content = zeit.content.cp.interfaces.ICMSContentIterable(auto)
            self.assertEqual(
                ['http://xml.zeit.de/testcontent'],
                [x.uniqueId for x in content])

    def test_stores_query_in_xml(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
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

    def test_prefers_raw_query_if_present(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.raw_query = 'raw'
        auto.automatic = True
        with mock.patch('zeit.find.search.search') as search:
            search.return_value = []
            auto.values()
            self.assertEqual('raw', search.call_args[0][0])

    def test_builds_query_from_conditions(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.query = (
            ('Channel', 'International', 'Nahost'),
            ('Channel', 'Wissen', None),
            ('Keyword', 'Berlin', None))
        auto.automatic = True
        with mock.patch('zeit.find.search.search') as search:
            search.return_value = []
            auto.values()
            query = search.call_args[0][0]
            self.assertIn('published:(published*)', query)
            self.assertIn(
                '(channels:(International*Nahost)'
                ' OR channels:(Wissen*)'
                ' OR keywords:(Berlin*))',
                query)

    def test_turning_automatic_off_materializes_filled_in_blocks(self):
        self.repository['normal'] = TestContentType()
        self.repository['leader'] = TestContentType()

        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 5
        auto.automatic = True
        zope.component.getAdapter(
            lead, zeit.edit.interfaces.IElementFactory, name='rss')()

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [dict(uniqueId='http://xml.zeit.de/normal'),
                                   dict(uniqueId='http://xml.zeit.de/leader',
                                        lead_candidate=True)]
            auto.automatic = False

        result = lead.values()
        self.assertEqual(
            ['teaser', 'teaser', 'rss'], [x.type for x in result])
        self.assertEqual(
            'http://xml.zeit.de/leader', list(result[0])[0].uniqueId)
        self.assertEqual(
            'http://xml.zeit.de/normal', list(result[1])[0].uniqueId)

    def test_checkin_smoke_test(self):
        with zeit.cms.checkout.helper.checked_out(self.repository['cp']) as cp:
            lead = cp['lead']
            auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
            auto.count = 1
            auto.automatic = True
