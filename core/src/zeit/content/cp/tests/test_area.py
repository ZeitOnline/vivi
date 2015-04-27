import StringIO
import zeit.content.cp.area
import zeit.content.cp.centerpage
import zeit.content.cp.testing


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
