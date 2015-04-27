from zeit.content.cp.blocks.teaser import apply_layout_for_added
from zeit.content.cp.centerpage import CenterPage
import lxml.etree
import mock
import zeit.cms.checkout.helper
import zeit.content.cp.testing
import zeit.edit.interfaces
import zope.component


class TestApplyLayout(zeit.content.cp.testing.FunctionalTestCase):
    """The event handler only works for the lead area (by purpose)."""

    def setUp(self):
        super(TestApplyLayout, self).setUp()
        self.cp = CenterPage()
        self.lead = self.cp['lead']
        self.teasers1 = self.lead.create_item('teaser')
        self.teasers2 = self.lead.create_item('teaser')
        self.teasers3 = self.lead.create_item('teaser')

    def test_block_should_have_same_layout_on_sort_to_position_1(self):
        self.teasers3.layout = zeit.content.cp.layout.get_layout('large')
        self.lead.updateOrder(
            [self.teasers3.__name__,
             self.teasers2.__name__,
             self.teasers1.__name__])
        self.assertEqual('large', self.teasers3.layout.id)

    def test_block_with_custom_layout_has_same_layout_on_sort_to_pos_1(self):
        self.teasers3.layout = zeit.content.cp.layout.get_layout('large')
        self.lead.updateOrder(
            [self.teasers3.__name__,
             self.teasers2.__name__,
             self.teasers1.__name__])
        self.assertEqual('large', self.teasers3.layout.id)

    def test_leader_should_become_buttons_on_sort_to_position_n(self):
        self.assertEqual('leader', self.teasers1.layout.id)
        self.lead.updateOrder(
            [self.teasers3.__name__,
             self.teasers2.__name__,
             self.teasers1.__name__])
        self.assertEqual('buttons', self.teasers1.layout.id)

    def test_block_with_custom_layout_is_overwritten_on_sort_to_pos_n(self):
        self.teasers1.layout = zeit.content.cp.layout.get_layout('large')
        self.lead.updateOrder(
            [self.teasers3.__name__,
             self.teasers2.__name__,
             self.teasers1.__name__])
        self.assertEqual('buttons', self.teasers1.layout.id)

    def test_xmlblock_should_take_lead_position_on_sort_to_position_1(self):
        xml = self.lead.create_item('xml')
        self.lead.updateOrder(
            [xml.__name__,
             self.teasers1.__name__,
             self.teasers2.__name__,
             self.teasers3.__name__])
        self.assertEqual('buttons', self.teasers1.layout.id)

    def test_layout_should_only_be_assigned_to_teasers(self):
        xml = self.lead.create_item('xml')
        self.lead.updateOrder(
            [self.teasers1.__name__,
             xml.__name__,
             self.teasers2.__name__,
             self.teasers3.__name__])
        self.assertFalse(hasattr(xml, 'layout'))

    def test_layouts_are_unchanged_if_position_1_untouched(self):
        self.teasers1.layout = zeit.content.cp.layout.get_layout('large')
        self.teasers2.layout = zeit.content.cp.layout.get_layout('large')
        self.teasers3.layout = zeit.content.cp.layout.get_layout('large')

        self.lead.updateOrder(
            [self.teasers1.__name__,
             self.teasers3.__name__,
             self.teasers2.__name__])

        self.assertEqual('large', self.teasers1.layout.id)
        self.assertEqual('large', self.teasers2.layout.id)
        self.assertEqual('large', self.teasers3.layout.id)

    def test_block_layout_should_remain_buttons_when_container_is_sorted(self):
        self.teasers1.layout = zeit.content.cp.layout.get_layout('buttons')
        self.lead.updateOrder(
            [self.teasers1.__name__,
             self.teasers2.__name__,
             self.teasers3.__name__])
        self.assertEqual('buttons', self.teasers1.layout.id)


class TestApplyLayoutForAdded(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(TestApplyLayoutForAdded, self).setUp()
        self.cp = CenterPage()
        self.added = mock.Mock()
        self.zca.patch_handler(
            self.added, zope.component.registry._getAdapterRequired(
                apply_layout_for_added, None))

    def test_apply_layout_for_added_is_called_for_new_teaser(self):
        self.cp['lead'].create_item('teaser')
        self.assertEqual(1, self.added.call_count)

    def test_apply_layout_for_added_is_not_called_for_non_teaser_blocks(self):
        self.cp['lead'].create_item('xml')
        self.assertEqual(0, self.added.call_count)

    def test_apply_layout_for_added_is_not_called_when_changing_containers(
            self):
        teaser = self.cp['lead'].create_item('teaser')
        self.assertEqual(1, self.added.call_count)
        del self.cp['lead'][teaser.__name__]
        self.assertEqual(1, self.added.call_count)
        self.cp['informatives'].add(teaser)
        self.assertEqual(1, self.added.call_count)

    def test_apply_layout_for_added_is_not_called_for_same_container(self):
        teaser = self.cp['lead'].create_item('teaser')
        self.assertEqual(1, self.added.call_count)
        del self.cp['lead'][teaser.__name__]
        self.assertEqual(1, self.added.call_count)
        self.cp['lead'].add(teaser)
        self.assertEqual(1, self.added.call_count)

    def test_new_teaser_list_on_position_1_has_layout_leader(self):
        lead = self.cp['lead']
        teaser1 = lead.create_item('teaser')
        self.assertEqual('leader', teaser1.layout.id)

    def test_new_teaser_list_on_position_n_has_layout_buttons(self):
        lead = self.cp['lead']
        lead.create_item('teaser')
        teaser2 = lead.create_item('teaser')
        self.assertEqual('buttons', teaser2.layout.id)


class TestDefaultLayout(zeit.content.cp.testing.FunctionalTestCase):
    """Test that the default layout for a teaser is set if None or invalid.

    Be aware that the teaser is added to informatives, i.e. the logic above for
    apply_layout will not be triggered (a guard makes sure it only works for
    the lead area).

    """

    def setUp(self):
        super(TestDefaultLayout, self).setUp()
        self.cp = CenterPage()
        self.lead = self.cp['lead']
        self.teaser = self.lead.create_item('teaser')

    def test_default_layout_is_set_for_new_teaser(self):
        area = self.cp['feature'].create_item('area')
        area.kind = 'duo'
        teaser = area.create_item('teaser')
        self.assertEqual(teaser.layout.id, 'two-side-by-side')
        self.assertEllipsis(
            '...module="two-side-by-side"...', lxml.etree.tostring(
                teaser.xml, pretty_print=True))

    def test_moving_teaser_sets_default_layout_for_new_area(self):
        self.teaser.layout = zeit.content.cp.layout.get_layout(
            'leader-two-columns')
        del self.cp['lead'][self.teaser.__name__]
        self.cp['informatives'].add(self.teaser)
        self.assertEllipsis('...module="leader"...', lxml.etree.tostring(
            self.teaser.xml, pretty_print=True))

    def test_moving_teaser_leaves_layout_alone_if_still_allowed(self):
        self.teaser.layout = zeit.content.cp.layout.get_layout('buttons')
        del self.cp['lead'][self.teaser.__name__]
        self.cp['informatives'].add(self.teaser)
        self.assertEllipsis('...module="buttons"...', lxml.etree.tostring(
            self.teaser.xml, pretty_print=True))
