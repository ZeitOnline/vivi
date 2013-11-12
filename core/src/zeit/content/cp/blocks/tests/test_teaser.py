# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.centerpage import CenterPage
import zeit.cms.checkout.helper
import zeit.content.cp.testing
import zeit.edit.interfaces
import zope.component
import zope.component


class TestApplyLayout(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(TestApplyLayout, self).setUp()
        self.cp = CenterPage()
        self.lead = self.cp['lead']
        self.teasers1 = self.factory()
        self.teasers2 = self.factory()
        self.teasers3 = self.factory()

    def factory(self, name='teaser'):
        factory = zope.component.getAdapter(
            self.lead,
            zeit.edit.interfaces.IElementFactory, name=name)
        return factory()

    def test_block_should_become_leader_on_sort_to_position_1(self):
        self.assertEqual('buttons', self.teasers3.layout.id)
        self.lead.updateOrder(
            [self.teasers3.__name__,
             self.teasers2.__name__,
             self.teasers1.__name__])
        self.assertEqual('leader', self.teasers3.layout.id)

    def test_leader_should_becom_buttons_on_sort_to_position_n(self):
        self.assertEqual('leader', self.teasers1.layout.id)
        self.lead.updateOrder(
            [self.teasers3.__name__,
             self.teasers2.__name__,
             self.teasers1.__name__])
        self.assertEqual('buttons', self.teasers1.layout.id)

    def test_xmlblock_should_take_lead_position_on_sort_to_position_1(self):
        xml = self.factory('xml')
        self.lead.updateOrder(
            [xml.__name__,
             self.teasers1.__name__,
             self.teasers2.__name__,
             self.teasers3.__name__])
        self.assertEqual('buttons', self.teasers1.layout.id)

    def test_layout_should_only_be_assigned_to_teasers(self):
        xml = self.factory('xml')
        self.lead.updateOrder(
            [self.teasers1.__name__,
             xml.__name__,
             self.teasers2.__name__,
             self.teasers3.__name__])
        self.assertFalse(hasattr(xml, 'layout'))


class AutopilotTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutopilotTest, self).setUp()
        self.repository['cp1'] = CenterPage()
        with zeit.cms.checkout.helper.checked_out(
                self.repository['cp1']) as cp:
            cp.topiclink_title = 'title'
            cp.topiclink_label_1 = 'label1'
            cp.topiclink_url_1 = 'url1'
        self.referenced_cp = self.repository['cp1']

        self.repository['cp2'] = zeit.content.cp.centerpage.CenterPage()
        self.cp = zeit.cms.checkout.interfaces.ICheckoutManager(
            self.repository['cp2']).checkout()
        self.teaser = zope.component.getAdapter(
            self.cp['informatives'],
            zeit.edit.interfaces.IElementFactory, name='teaser')()
        self.teaser.referenced_cp = self.repository['cp1']

    def test_includes_topiclinks_of_referenced_cp(self):
        self.assertEqual(
            self.referenced_cp.topiclink_title,
            self.teaser.xml.topiclinks.title)
        self.assertEqual(
            self.referenced_cp.topiclink_url_1,
            self.teaser.xml.topiclinks.topiclink.get('href'))
        self.assertEqual(
            self.referenced_cp.topiclink_label_1,
            self.teaser.xml.topiclinks.topiclink)

    def test_nothing_referenced_has_no_topiclinks_node(self):
        self.teaser.referenced_cp = None
        self.assertNotIn('topiclinks', self.teaser.xml)

    def test_setting_reference_multiple_times_creates_only_one_topiclink_node(
            self):
        self.teaser.referenced_cp = self.repository['cp1']
        self.assertEqual(1, len(self.teaser.xml.xpath('topiclinks')))

    def test_topiclinks_are_updated_on_checkin(self):
        with zeit.cms.checkout.helper.checked_out(
                self.repository['cp1']) as cp:
            cp.topiclink_label_1 = 'label2'
        cp = zeit.cms.checkout.interfaces.ICheckinManager(self.cp).checkin()
        self.assertEqual(
            'label2', cp['informatives'].values()[-1].xml.topiclinks.topiclink)


class SuppressImagePositionsTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(SuppressImagePositionsTest, self).setUp()
        self.cp = CenterPage()
        self.teaser = zope.component.getAdapter(
            self.cp['lead'],
            zeit.edit.interfaces.IElementFactory, name='teaser')()

    def test_attribute_not_present_returns_empty_list(self):
        self.assertEqual([], self.teaser.suppress_image_positions)

    def test_setting_to_empty_value_removes_attribute(self):
        self.teaser.suppress_image_positions = []
        ABSENT = object()
        self.assertEqual(
            ABSENT, self.teaser.xml.get('suppress-image-positions', ABSENT))

    def test_stores_list_comma_separated_with_index_starting_at_1(self):
        self.teaser.suppress_image_positions = [3, 4]
        self.assertEqual([3, 4], self.teaser.suppress_image_positions)
        self.assertEqual(
            '4,5', self.teaser.xml.get('suppress-image-positions'))
