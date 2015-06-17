import StringIO
import mock
import zeit.content.cp.area
import zeit.content.cp.centerpage
import zeit.content.cp.testing
import zope.lifecycleevent


CENTERPAGE = """
<centerpage
  xmlns:cp="http://namespaces.zeit.de/CMS/cp"
  xmlns:py="http://codespeak.net/lxml/objectify/pytype"
  xmlns:xi="http://www.w3.org/2001/XInclude"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <head/>
  <body>
    <cluster area="feature">
      <region area="lead"/>
      <region area="informatives"/>
    </cluster>
    <cluster area="teaser-mosaic">
      {content}
    </cluster>
  </body>
  <feed/>
</centerpage>
"""

TEASERBAR = """
<region cp:type="teaser-bar" module="dmr" area="teaser-row-full"
        cp:__name__="{uuid}" supertitle="asd" teaserText="qwe"
        background_color="ff"/>
"""


class TeaserBarBackwardCompatibilityTest(
        zeit.content.cp.testing.FunctionalTestCase):

    def test_can_read_old_xml_with_teaser_bar_and_creates_areas(self):
        cp = zeit.content.cp.centerpage.CenterPage(StringIO.StringIO(
            CENTERPAGE.format(content=TEASERBAR.format(uuid='FOO'))))
        self.assertIsInstance(
            cp['teaser-mosaic']['FOO'], zeit.content.cp.area.Area)

    def test_can_read_old_xml_and_recognizes_teaserbar_ids_correctly(self):
        cp = zeit.content.cp.centerpage.CenterPage(StringIO.StringIO(
            CENTERPAGE.format(content=(
                TEASERBAR.format(uuid='FOO')
                + TEASERBAR.format(uuid='BAR')))))
        self.assertEqual(['FOO', 'BAR'], cp['teaser-mosaic'].keys())


class OverflowBlocks(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(OverflowBlocks, self).setUp()
        self.cp = zeit.content.cp.centerpage.CenterPage()
        self.region = self.cp.create_item('region')
        self.area1 = self.region.create_item('area')
        self.area2 = self.region.create_item('area')

        self.area1.block_max = 1
        self.area1.overflow_into = self.area2

    def test_adding_more_than_max_blocks_overflows_the_newly_added_block(self):
        t1 = self.area1.create_item('teaser').__name__
        t2 = self.area1.create_item('teaser').__name__
        self.assertEqual([t1], self.area1.keys())
        self.assertEqual([t2], self.area2.keys())

    def test_blocks_overflow_into_beginning_of_overflow_area(self):
        t1 = self.area1.create_item('teaser').__name__
        t2 = self.area1.create_item('teaser').__name__
        t3 = self.area1.create_item('teaser').__name__
        self.assertEqual([t1], self.area1.keys())
        # added t3 last, so should be first in overflow area
        self.assertEqual([t3, t2], self.area2.keys())

    def test_inserting_blocks_on_top_will_overflow_existing_block(self):
        t1 = self.area1.create_item('teaser', position=0).__name__
        t2 = self.area1.create_item('teaser', position=0).__name__
        t3 = self.area1.create_item('teaser', position=0).__name__
        # inserted t3 last, so should be the only teaser in area1
        self.assertEqual([t3], self.area1.keys())
        self.assertEqual([t2, t1], self.area2.keys())

    def test_apply_layout_for_lead_area_works_with_overflow(self):
        """Test add and insert(0) when the apply_layout logic is active."""
        self.area1.__name__ = 'lead'
        t1 = self.area1.create_item('teaser').__name__
        t2 = self.area1.create_item('teaser', position=0).__name__
        t3 = self.area1.create_item('teaser').__name__
        self.assertEqual([t2], self.area1.keys())
        self.assertEqual([t3, t1], self.area2.keys())

    def test_setting_overflow_into_none_is_allowed(self):
        self.area1.overflow_into = None
        self.assertEqual(None, self.area1.overflow_into)

    def test_overflow_works_across_multiple_areas(self):
        self.area3 = self.region.create_item('area')
        self.area2.block_max = 1
        self.area2.overflow_into = self.area3
        t1 = self.area1.create_item('teaser').__name__
        t2 = self.area1.create_item('teaser').__name__
        t3 = self.area1.create_item('teaser').__name__
        self.assertEqual([t1], self.area1.keys())
        # added t3 last, so should be first in overflow area
        self.assertEqual([t3], self.area2.keys())
        self.assertEqual([t2], self.area3.keys())

    def test_moving_area_below_target_removes_overflow(self):
        region2 = self.cp.create_item('region')
        del self.region[self.area1.__name__]
        region2.add(self.area1)
        self.assertEqual(None, self.area1.overflow_into)

    def test_moving_target_above_area_removes_overflow(self):
        region2 = self.cp.create_item('region')
        del self.region[self.area2.__name__]
        region2.add(self.area2)

        del region2[self.area2.__name__]
        self.region.insert(0, self.area2)
        self.assertEqual(None, self.area1.overflow_into)

    def test_moving_areas_with_proper_order_keeps_overflow(self):
        region2 = self.cp.create_item('region')
        del self.region[self.area2.__name__]
        region2.insert(0, self.area2)
        del self.region[self.area1.__name__]
        region2.insert(0, self.area1)
        self.assertNotEqual(None, self.area1.overflow_into)

    def test_sorting_areas_removes_overflow_if_ordered_wrong(self):
        self.region.updateOrder([self.area2.__name__, self.area1.__name__])
        self.assertEqual(None, self.area1.overflow_into)

    def test_reducing_block_max_overflows_excessive_blocks(self):
        self.area1.block_max = 2
        t1 = self.area1.create_item('teaser').__name__
        t2 = self.area1.create_item('teaser').__name__
        self.area1.block_max = 1
        zope.lifecycleevent.modified(
            self.area1, zope.lifecycleevent.Attributes(
                zeit.content.cp.interfaces.IArea, 'block_max'))
        self.assertEqual([t1], self.area1.keys())
        self.assertEqual([t2], self.area2.keys())


class AutomaticAreaTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticAreaTest, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()

    def test_fills_with_placeholders_when_set_to_automatic(self):
        lead = self.repository['cp']['lead']
        lead.count = 5
        lead.automatic = True
        lead.automatic_type = 'query'
        self.assertEqual(5, len(lead))

    def test_fills_with_placeholders_when_teaser_count_changed(self):
        lead = self.repository['cp']['lead']
        lead.count = 5
        lead.automatic = True
        lead.automatic_type = 'query'
        self.assertEqual(5, len(lead))
        lead.count = 7
        self.assertEqual(7, len(lead))

    def test_enabling_automatic_preserves_layout(self):
        lead = self.repository['cp']['lead']
        teaser = lead.create_item('teaser')
        teaser.layout = zeit.content.cp.layout.get_layout('two-side-by-side')
        lead.count = 1
        lead.automatic = True
        self.assertEqual('two-side-by-side', lead.values()[0].layout.id)

    def test_disabling_automatic_preserves_all_teaser_fields(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        auto = lead.values()[0]
        auto.layout = zeit.content.cp.layout.get_layout('two-side-by-side')
        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent')]
            lead.automatic = False
        self.assertEqual('two-side-by-side', lead.values()[0].layout.id)
