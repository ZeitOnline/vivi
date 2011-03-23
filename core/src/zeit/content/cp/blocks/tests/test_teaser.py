# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.testing


class TestApplyLayout(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(TestApplyLayout, self).setUp()
        import zeit.content.cp.centerpage
        self.cp = zeit.content.cp.centerpage.CenterPage()
        self.lead = self.cp['lead']
        self.teasers1 = self.factory()
        self.teasers2 = self.factory()
        self.teasers3 = self.factory()

    def factory(self, name='teaser'):
        import zeit.content.cp.interfaces
        import zope.component
        factory = zope.component.getAdapter(
            self.lead,
            zeit.content.cp.interfaces.IElementFactory, name=name)
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
