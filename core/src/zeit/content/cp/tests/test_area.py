import lxml.etree
import zope.lifecycleevent

import zeit.cms.testing
import zeit.content.cp.testing


class AutomaticAreaTest(zeit.content.cp.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()

    def test_fills_with_placeholders_when_set_to_automatic(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 5
        lead.automatic = True
        lead.automatic_type = 'query'
        self.assertEqual(5, len(lead))

    def test_fills_with_placeholders_when_teaser_count_changed(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 5
        lead.automatic = True
        lead.automatic_type = 'query'
        self.assertEqual(5, len(lead))
        lead.count = 7
        self.assertEqual(7, len(lead))

    def test_enabling_automatic_preserves_layout(self):
        lead = self.repository['cp'].body['lead']
        teaser = lead.create_item('teaser')
        teaser.volatile = True
        teaser.read_more = 'foo'
        teaser.layout = zeit.content.cp.layout.get_layout('two-side-by-side')
        lead.count = 1
        lead.automatic = True
        self.assertEqual(None, lead.values()[0].read_more)
        self.assertEqual('two-side-by-side', lead.values()[0].layout.id)

    def test_disabling_automatic_preserves_all_teaser_fields(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 1
        lead.automatic = True
        auto = lead.values()[0]
        auto.read_more = 'foo'
        auto.layout = zeit.content.cp.layout.get_layout('two-side-by-side')
        lead.automatic = False
        self.assertEqual('foo', lead.values()[0].read_more)
        self.assertEqual('two-side-by-side', lead.values()[0].layout.id)

    def test_materializing_autopilot_marks_previous_automatic_teasers(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 1
        lead.automatic = True
        lead.automatic = False
        [teaser] = lead.values()
        self.assertEqual(True, teaser.volatile)

    def test_adding_teaser_by_hand_uses_default_for_volatile(self):
        lead = self.repository['cp'].body['lead']
        teaser = lead.create_item('teaser')
        # assertFalse accepts None as well, so we use assertEqual explicitly
        self.assertEqual(False, teaser.volatile)

    def test_materializing_autopilot_keeps_manual_content(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 0
        lead.automatic = True
        manual_teaser = lead.create_item('teaser')

        lead.automatic = False
        self.assertEqual(1, len(lead))
        self.assertEqual([manual_teaser], lead.values())

    def test_changing_automatic_count_also_counts_manual_content(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 2
        lead.automatic = True

        manual_teaser = lead.create_item('teaser')
        self.assertEqual(2, len(lead))

        lead.count = 1
        self.assertEqual(1, len(lead))
        self.assertEqual([manual_teaser], lead.values())

        lead.count = 3
        self.assertEqual(3, len(lead))
        self.assertEqual(manual_teaser, lead.values()[0])

    def test_changing_automatic_count_only_counts_teaser_modules(self):
        lead = self.repository['cp'].body['lead']
        lead.create_item('markup')
        lead.count = 2
        lead.automatic = True
        self.assertEqual(['markup', 'auto-teaser', 'auto-teaser'], [x.type for x in lead.values()])

    def test_reducing_automatic_count_does_not_delete_manual_content(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 1
        lead.automatic = True
        manual_teaser = lead.create_item('teaser')

        lead.count = 0
        self.assertEqual(1, len(lead))
        self.assertEqual([manual_teaser], lead.values())

    def test_autopilot_allows_more_manual_content_than_automatic_count(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 1
        lead.automatic = True
        teaser1 = lead.create_item('teaser')
        teaser2 = lead.create_item('teaser')
        self.assertEqual(2, len(lead))
        self.assertEqual([teaser1, teaser2], lead.values())

    def test_adding_manual_teaser_automatically_removes_last_auto_teaser(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 2
        lead.automatic = True
        auto_teaser1, auto_teaser2 = lead.values()
        manual_teaser = lead.create_item('teaser')
        self.assertEqual([auto_teaser1, manual_teaser], lead.values())

    def test_removing_manual_teaser_automatically_adds_auto_teaser(self):
        from zeit.content.cp.interfaces import IAutomaticTeaserBlock

        lead = self.repository['cp'].body['lead']
        lead.count = 2
        lead.automatic = True
        manual_teaser1 = lead.create_item('teaser')
        manual_teaser2 = lead.create_item('teaser')
        self.assertEqual([manual_teaser1, manual_teaser2], lead.values())

        del lead[manual_teaser1.__name__]
        self.assertNotIn(manual_teaser1, lead.values())
        self.assertIn(manual_teaser2, lead.values())
        self.assertTrue(IAutomaticTeaserBlock.providedBy(lead.values()[-1]))

    def test_enabling_automatic_removes_all_auto_generated_blocks(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 1
        teaser = lead.create_item('teaser')
        teaser.volatile = True  # generated by AutoPilot
        lead.automatic = True
        self.assertEqual(['auto-teaser'], [x.type for x in lead.values()])

    def test_enabling_automatic_keeps_blocks_not_added_by_autopilot(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 1
        teaser = lead.create_item('teaser')
        teaser.volatile = False  # not generated by AutoPilot
        lead.automatic = True
        self.assertEqual([teaser], lead.values())

    def test_enabling_automatic_keeps_order_of_manually_placed_blocks(self):
        lead = self.repository['cp'].body['lead']
        lead.count = 3

        teaser1 = lead.create_item('teaser')
        teaser1.volatile = True
        teaser2 = lead.create_item('teaser')
        teaser2.volatile = False
        teaser3 = lead.create_item('teaser')
        teaser3.volatile = True

        lead.automatic = True
        self.assertEqual(['auto-teaser', 'teaser', 'auto-teaser'], [x.type for x in lead.values()])

    def test_enabling_automatic_does_not_break_on_updateOrder(self):
        """update_autopilot handler might interfere and creates new blocks"""
        lead = self.repository['cp'].body['lead']
        lead.count = 3
        teaser = lead.create_item('teaser')
        teaser.volatile = True

        with self.assertNothingRaised():
            lead.automatic = True

    def test_disabling_automatic_keeps_order_of_teasers(self):
        from zeit.cms.testcontenttype.testcontenttype import ExampleContentType

        self.repository['t1'] = ExampleContentType()
        self.repository['t2'] = ExampleContentType()

        lead = self.repository['cp'].body['lead']
        lead.count = 2
        lead.automatic = True
        lead.create_item('teaser')
        lead.count = 3

        order = lead.keys()
        lead.automatic = False
        self.assertEqual(order, lead.keys())


class AreaDelegateTest(zeit.content.cp.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.area = self.repository['cp'].body['feature'].create_item('area')
        other = zeit.content.cp.centerpage.CenterPage()
        other.title = 'referenced'
        other.supertitle = 'supertitle'
        other.topiclink_label_1 = 'foo'
        other.topiclink_url_1 = 'example.com'
        self.repository['other'] = other
        self.area.referenced_cp = self.repository['other']
        zope.lifecycleevent.modified(
            self.area,
            zope.lifecycleevent.Attributes(zeit.content.cp.interfaces.IArea, 'referenced_cp'),
        )

    def test_attributes_from_referenced_cp_are_copied(self):
        self.assertEqual('referenced', self.area.title)
        self.assertEqual('supertitle', self.area.supertitle)

    def test_local_value_takes_precendence(self):
        self.assertEqual('referenced', self.area.title)
        self.area.title = 'local'
        self.assertEqual('local', self.area.title)

    def test_local_value_is_not_overwritten(self):
        self.area.title = 'local'
        self.assertEqual('local', self.area.title)
        zope.lifecycleevent.modified(
            self.area,
            zope.lifecycleevent.Attributes(zeit.content.cp.interfaces.IArea, 'referenced_cp'),
        )
        self.assertEqual('local', self.area.title)

    def test_read_more_url_is_generated_from_cp(self):
        self.assertEqual('http://localhost/live-prefix/other', self.area.read_more_url)

    def test_topiclink_values_from_referenced_cp_are_used(self):
        self.assertEqual('foo', self.area.topiclink_label_1)
        self.assertEqual('example.com', self.area.topiclink_url_1)

    def test_topiclink_values_can_be_overwritten(self):
        self.area.topiclink_label_1 = 'bar'
        self.area.topiclink_url_1 = 'https://zeit.de'
        self.assertEqual('bar', self.area.topiclink_label_1)
        self.assertEqual('https://zeit.de', self.area.topiclink_url_1)

    def test_untouched_topiclink_value_reacts_to_change_on_referenced_cp(self):
        self.area.topiclink_label_1 = 'bar'
        self.area.referenced_cp.topiclink_url_1 = 'https://foo.bar'
        self.area.referenced_cp.topiclink_label_1 = 'foo'
        self.assertEqual('bar', self.area.topiclink_label_1)
        self.assertEqual('https://foo.bar', self.area.topiclink_url_1)

    def test_set_area_background_color(self):
        self.area.background_color = '#000000'
        self.assertEqual('#000000', self.area.background_color)


class CustomQueryTest(zeit.content.cp.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()

    def test_serializes_via_dav_converter(self):
        area = self.repository['cp'].body['lead']
        source = zeit.cms.content.interfaces.ICommonMetadata['serie'].source(None)
        autotest = source.find('Autotest')
        area.query = (('serie', 'eq', autotest),)
        self.assertEllipsis(
            '<query...><condition...type="serie"...>Autotest</condition></query>',
            lxml.etree.tostring(area.xml.find('query'), encoding=str),
        )
        self.assertEqual((('serie', 'eq', autotest),), area.query)
