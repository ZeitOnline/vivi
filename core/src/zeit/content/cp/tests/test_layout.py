import zeit.content.cp.centerpage
import zeit.content.cp.testing


class TestDefaultLayout(zeit.content.cp.testing.FunctionalTestCase):

    def test_default_layout_of_1_2_two_side_by_side(self):
        centerpage = zeit.content.cp.centerpage.CenterPage()
        region = centerpage.create_item('region')
        area = region.create_item('area')

        area.width = '1/2'
        teaser = area.create_item('teaser')
        self.assertEqual(teaser.layout.id, 'two-side-by-side')
