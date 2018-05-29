# coding: utf-8
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.content.cp.interfaces import IRenderedArea
import json
import lxml.etree
import mock
import pysolr
import transaction
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.automatic
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zeit.edit.interfaces
import zeit.retresco.content
import zeit.retresco.interfaces
import zeit.solr.interfaces
import zope.component


class AutomaticAreaSolrTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticAreaSolrTest, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)

    def tests_values_contain_only_blocks_with_content(self):
        lead = self.repository['cp']['lead']
        lead.count = 5
        lead.automatic = True
        lead.automatic_type = 'query'
        self.solr.search.return_value = pysolr.Results([], 0)
        self.assertEqual(0, len(IRenderedArea(lead).values()))

    def tests_ignores_items_with_errors(self):
        lead = self.repository['cp']['lead']
        lead.count = 2
        lead.automatic = True
        lead.automatic_type = 'query'

        return_values = [pysolr.Results([
            dict(uniqueId='http://xml.zeit.de/notfound'),
            dict(uniqueId='http://xml.zeit.de/testcontent')], 2),
            pysolr.Results([], 0)
        ]
        self.solr.search.side_effect = lambda *args, **kw: return_values.pop(0)
        self.assertEqual(1, len(IRenderedArea(lead).values()))

    def test_only_marked_articles_are_put_into_leader_block(self):
        self.repository['normal'] = ExampleContentType()
        leader = ExampleContentType()
        leader.lead_candidate = True
        self.repository['leader'] = leader

        lead = self.repository['cp']['lead']
        lead.count = 2
        lead.automatic = True
        lead.automatic_type = 'query'

        self.solr.search.return_value = pysolr.Results([
            dict(uniqueId='http://xml.zeit.de/normal'),
            dict(uniqueId='http://xml.zeit.de/leader')], 2)
        result = IRenderedArea(lead).values()
        self.assertEqual(
            'http://xml.zeit.de/leader', list(result[0])[0].uniqueId)
        self.assertEqual(
            'http://xml.zeit.de/normal', list(result[1])[0].uniqueId)

    def test_no_marked_articles_available_leader_block_gets_normal_article(
            self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.automatic_type = 'query'

        self.solr.search.return_value = pysolr.Results([
            dict(uniqueId='http://xml.zeit.de/testcontent')], 1)
        result = IRenderedArea(lead).values()
        leader = result[0]
        self.assertEqual(
            'http://xml.zeit.de/testcontent', list(leader)[0].uniqueId)

    def test_no_marked_articles_leader_block_layout_is_changed_virtually(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.automatic_type = 'query'

        self.solr.search.return_value = pysolr.Results([
            dict(uniqueId='http://xml.zeit.de/testcontent')], 1)
        result = IRenderedArea(lead).values()
        leader = result[0]
        self.assertEqual('buttons', leader.layout.id)
        self.assertEqual('leader', lead.values()[0].layout.id)
        self.assertEllipsis('...module="buttons"...', lxml.etree.tostring(
            zeit.content.cp.interfaces.IRenderedXML(leader),
            pretty_print=True))

    def test_leader_block_takes_everything_if_area_configured(self):
        self.repository['normal'] = ExampleContentType()
        leader = ExampleContentType()
        leader.lead_candidate = True
        self.repository['leader'] = leader

        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.require_lead_candidates = False
        lead.automatic = True
        lead.automatic_type = 'query'

        self.solr.search.return_value = pysolr.Results([
            dict(uniqueId='http://xml.zeit.de/normal'),
            dict(uniqueId='http://xml.zeit.de/leader')], 2)
        result = IRenderedArea(lead).values()
        self.assertEqual(
            'http://xml.zeit.de/normal', list(result[0])[0].uniqueId)

    def test_renders_xml_with_filled_in_blocks(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.automatic_type = 'query'

        self.solr.search.return_value = pysolr.Results([
            dict(uniqueId='http://xml.zeit.de/testcontent',
                 lead_candidate=True)], 1)
        xml = zeit.content.cp.interfaces.IRenderedXML(lead)
        self.assertEllipsis(
            """\
<region...>
  <container...type="teaser"...>
    <block...href="http://xml.zeit.de/testcontent"...""",
            lxml.etree.tostring(xml, pretty_print=True))

    def test_cms_content_iter_returns_filled_in_blocks(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.automatic_type = 'query'

        self.solr.search.return_value = pysolr.Results([
            dict(uniqueId='http://xml.zeit.de/testcontent',
                 lead_candidate=True)], 1)
        content = zeit.edit.interfaces.IElementReferences(lead)
        self.assertEqual(
            ['http://xml.zeit.de/testcontent'],
            [x.uniqueId for x in content])

    def test_stores_query_in_xml(self):
        lead = self.repository['cp']['lead']
        self.assertEqual((), lead.query)
        lead.query = (
            ('channels', 'International', 'Nahost'),
            ('channels', 'Wissen', None))
        self.assertEllipsis(
            """<...
            <query>
              <condition...type="channels"...>International Nahost</condition>
              <condition...type="channels"...>Wissen</condition>
            </query>...""", lxml.etree.tostring(lead.xml, pretty_print=True))

    def test_which_query_data_is_used_depends_on_automatic_type(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.raw_query = 'raw'
        lead.automatic_type = 'query'
        self.solr.search.return_value = pysolr.Results([], 0)
        IRenderedArea(lead).values()
        self.assertEqual('raw', self.solr.search.call_args[0][0])

    def test_raw_query_order_defaults_to_first_released(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.raw_query = 'raw'
        lead.automatic_type = 'query'
        self.solr.search.return_value = pysolr.Results([], 0)
        IRenderedArea(lead).values()
        self.assertEqual(
            'date-first-released desc', self.solr.search.call_args[1]['sort'])

    def test_raw_query_order_can_be_set(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.raw_query = 'raw'
        lead.raw_order = 'order'
        lead.automatic_type = 'query'
        self.solr.search.return_value = pysolr.Results([], 0)
        IRenderedArea(lead).values()
        self.assertEqual('order', self.solr.search.call_args[1]['sort'])

    def test_returns_no_content_on_solr_error(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.raw_query = 'raw'
        lead.automatic_type = 'query'
        self.solr.search.side_effect = RuntimeError('provoked')
        auto = IRenderedArea(lead)
        self.assertEqual(0, len(auto.values()))
        self.assertEqual(0, auto._content_query.total_hits)

    def test_turning_automatic_off_materializes_filled_in_blocks(self):
        self.repository['normal'] = ExampleContentType()
        leader = ExampleContentType()
        leader.lead_candidate = True
        self.repository['leader'] = leader

        lead = self.repository['cp']['lead']
        lead.count = 5
        lead.automatic = True
        lead.automatic_type = 'query'
        zope.component.getAdapter(
            lead, zeit.edit.interfaces.IElementFactory, name='xml')()

        empty = pysolr.Results([], 0)
        return_values = [pysolr.Results([
            dict(uniqueId='http://xml.zeit.de/normal'),
            dict(uniqueId='http://xml.zeit.de/leader')], 2),
            empty, empty, empty
        ]
        self.solr.search.side_effect = lambda *args, **kw: return_values.pop(0)
        lead.automatic = False

        result = lead.values()
        self.assertEqual(
            ['teaser', 'teaser', 'xml'], [x.type for x in result])
        self.assertEqual(
            'http://xml.zeit.de/leader', list(result[0])[0].uniqueId)
        self.assertEqual(
            'http://xml.zeit.de/normal', list(result[1])[0].uniqueId)

    def test_checkin_smoke_test(self):
        self.solr.search.return_value = pysolr.Results([], 0)
        with zeit.cms.checkout.helper.checked_out(self.repository['cp']) as cp:
            lead = cp['lead']
            lead.count = 1
            lead.automatic = True
            lead.automatic_type = 'query'


class AutomaticAreaElasticsearchTest(
        zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticAreaElasticsearchTest, self).setUp()
        self.cp = zeit.content.cp.centerpage.CenterPage()
        self.area = self.cp['feature'].create_item('area')
        self.area.count = 3
        self.area.automatic = True
        self.area.automatic_type = 'elasticsearch-query'
        self.repository['cp'] = self.cp
        self.elasticsearch = zope.component.getUtility(
            zeit.retresco.interfaces.IElasticsearch)

    def test_it_returns_no_content_on_elasticsearch_error(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.elasticsearch_raw_query = '{"query": {}}'
        lead.automatic_type = 'elasticsearch-query'
        self.elasticsearch.search.side_effect = RuntimeError('provoked')
        auto = IRenderedArea(lead)
        self.assertEqual(0, len(auto.values()))
        self.assertEqual(0, auto._content_query.total_hits)

    def test_it_returns_content_objects_provided_by_elasticsearch(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.elasticsearch_raw_query = (
            u'{"query": {"match": {"title": "üüü"}}}')
        lead.automatic_type = 'elasticsearch-query'
        result = zeit.cms.interfaces.Result(
            [{'url': '/cp'},
             {'uniqueId': '/i-do-not-exist'}])
        result.hits = 4711
        self.elasticsearch.search.return_value = result
        auto = IRenderedArea(lead)
        self.assertEqual(1, len(auto.values()))
        self.assertEqual(4711, auto._content_query.total_hits)

        self.assertEqual(
            (({'query': {'bool': {'filter': [
                {u'match': {u'title': u'üüü'}},
                {'term': {'payload.workflow.published': True}}]}}},
              u'payload.document.date_first_released:desc'),
             dict(start=0, rows=1, include_payload=False)),
            self.elasticsearch.search.call_args)

    def test_builds_query_from_conditions(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        source = zeit.cms.content.interfaces.ICommonMetadata['serie'].source(
            None)
        autotest = source.find('Autotest')
        lead.query = (('serie', autotest),)
        lead.automatic = True
        lead.automatic_type = 'channel'
        self.elasticsearch.search.return_value = zeit.cms.interfaces.Result()
        IRenderedArea(lead).values()
        self.assertEqual({'query': {'bool': {'filter': [
            {'term': {'payload.document.serie': 'Autotest'}},
            {'term': {'payload.workflow.published': True}}]}}},
            self.elasticsearch.search.call_args[0][0])

    def test_builds_query_with_elasticsearch_fieldname_exceptions(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.query = (
            ('channels', 'International', 'Nahost'),
            ('channels', 'Wissen', None))
        lead.automatic = True
        lead.automatic_type = 'channel'
        self.elasticsearch.search.return_value = zeit.cms.interfaces.Result()
        IRenderedArea(lead).values()
        self.assertEqual({'query': {'bool': {'filter': [
            {'bool': {'should': [
                {'term': {'payload.document.channels.hierarchy':
                          'International Nahost'}},
                {'term': {'payload.document.channels.hierarchy':
                          'Wissen'}},
            ]}},
            {'term': {'payload.workflow.published': True}}]}}},
            self.elasticsearch.search.call_args[0][0])

    def test_builds_query_with_condition_exception(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.query = (
            ('ressort', 'International', 'Nahost'),
            ('ressort', 'Wissen', None))
        lead.automatic = True
        lead.automatic_type = 'channel'
        self.elasticsearch.search.return_value = zeit.cms.interfaces.Result()
        IRenderedArea(lead).values()
        self.assertEqual({'query': {'bool': {'filter': [
            {'bool': {'should': [
                {'bool': {'must': [
                    {'term': {'payload.document.ressort': 'International'}},
                    {'term': {'payload.document.sub_ressort': 'Nahost'}},
                ]}},
                {'term': {'payload.document.ressort':
                          'Wissen'}},
            ]}},
            {'term': {'payload.workflow.published': True}}]}}},
            self.elasticsearch.search.call_args[0][0])

    def test_joins_different_fields_with_AND_but_same_fields_with_OR(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        source = zeit.cms.content.interfaces.ICommonMetadata['serie'].source(
            None)
        autotest = source.find('Autotest')
        lead.query = (
            ('channels', 'International', 'Nahost'),
            ('channels', 'Wissen', None),
            ('serie', autotest),
            ('ressort', 'Wissen', None))
        lead.automatic = True
        lead.automatic_type = 'channel'
        self.elasticsearch.search.return_value = zeit.cms.interfaces.Result()
        IRenderedArea(lead).values()
        self.assertEqual({'query': {'bool': {'filter': [
            {'bool': {'should': [
                {'term': {'payload.document.channels.hierarchy':
                          'International Nahost'}},
                {'term': {'payload.document.channels.hierarchy':
                          'Wissen'}},
            ]}},
            {'term': {'payload.document.ressort': 'Wissen'}},
            {'term': {'payload.document.serie': 'Autotest'}},
            {'term': {'payload.workflow.published': True}}]}}},
            self.elasticsearch.search.call_args[0][0])

    def test_can_take_over_whole_query_body(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.elasticsearch_raw_query = (
            '{"query": {"match": {"title": "foo"}}}')
        lead.is_complete_query = True
        lead.automatic_type = 'elasticsearch-query'
        self.elasticsearch.search.return_value = zeit.cms.interfaces.Result()
        IRenderedArea(lead).values()
        self.assertEqual(
            json.loads(lead.elasticsearch_raw_query),
            self.elasticsearch.search.call_args[0][0])

    def test_adds_hide_dupes_clause_to_whole_query_body(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.elasticsearch_raw_query = (
            '{"query": {"match": {"title": "foo"}}}')
        lead.is_complete_query = True
        lead.automatic_type = 'elasticsearch-query'
        self.elasticsearch.search.return_value = zeit.cms.interfaces.Result()
        auto = IRenderedArea(lead)
        auto._content_query.hide_dupes_clause = {'ids': {'values': ['id1']}}
        auto.values()
        self.assertEqual(
            {"query": {"bool": {
                "must": {"query": {"match": {"title": "foo"}}},
                "must_not": {"ids": {"values": ["id1"]}}}}},
            self.elasticsearch.search.call_args[0][0])

    def test_query_order_defaults_to_semantic_publish(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.query = (('channels', 'International', 'Nahost'),)
        lead.automatic = True
        lead.automatic_type = 'channel'
        self.elasticsearch.search.return_value = zeit.cms.interfaces.Result()
        IRenderedArea(lead).values()
        self.assertEqual(
            'payload.workflow.date_last_published_semantic:desc',
            self.elasticsearch.search.call_args[0][1])

    def test_query_order_can_be_set(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.query = (('channels', 'International', 'Nahost'),)
        lead.query_order = 'order'
        lead.automatic = True
        lead.automatic_type = 'channel'
        self.elasticsearch.search.return_value = zeit.cms.interfaces.Result()
        IRenderedArea(lead).values()
        self.assertEqual('order', self.elasticsearch.search.call_args[0][1])


class AutomaticAreaTopicpageTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticAreaTopicpageTest, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.tms = mock.Mock()
        self.zca.patch_utility(self.tms, zeit.retresco.interfaces.ITMS)

    def test_passes_id_to_tms(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.referenced_topicpage = 'tms-id'
        lead.automatic_type = 'topicpage'
        self.tms.get_topicpage_documents.return_value = (
            zeit.cms.interfaces.Result())
        IRenderedArea(lead).values()
        args, kw = self.tms.get_topicpage_documents.call_args
        self.assertEqual('tms-id', kw['id'])

    def test_returns_no_content_on_tms_error(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.referenced_topicpage = 'tms-id'
        lead.automatic_type = 'topicpage'
        self.tms.get_topicpage_documents.side_effect = RuntimeError('provoked')
        auto = IRenderedArea(lead)
        self.assertEqual(0, len(auto.values()))
        self.assertEqual(0, auto._content_query.total_hits)

    def test_filter_can_be_set(self):
        lead = self.repository['cp']['lead']
        lead.count = 1
        lead.automatic = True
        lead.referenced_topicpage = 'tms-id'
        lead.automatic_type = 'topicpage'
        lead.topicpage_filter = 'has_image'
        self.tms.get_topicpage_documents.return_value = (
            zeit.cms.interfaces.Result())
        IRenderedArea(lead).values()
        self.assertEqual(
            'has_image',
            self.tms.get_topicpage_documents.call_args[1]['filter'])


class AutomaticAreaCenterPageTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticAreaCenterPageTest, self).setUp()
        self.cp = zeit.content.cp.centerpage.CenterPage()
        self.area = self.cp['feature'].create_item('area')
        self.repository['cp'] = self.cp

        t1 = self.create_content('t1', 't1')
        t2 = self.create_content('t2', 't2')
        t3 = self.create_content('t3', 't3')
        cp_with_teaser = self.create_and_checkout_centerpage(
            name='cp_with_teaser', contents=[t1, t2, t3])
        zeit.cms.checkout.interfaces.ICheckinManager(cp_with_teaser).checkin()

        self.area.referenced_cp = self.repository['cp_with_teaser']
        self.area.count = 3
        self.area.automatic = True
        self.area.automatic_type = 'centerpage'

        self.solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)

    def test_returns_teasers_from_referenced_center_page(self):
        self.assertEqual([
            'http://xml.zeit.de/t1',
            'http://xml.zeit.de/t2',
            'http://xml.zeit.de/t3'],
            [list(x)[0].uniqueId for x in IRenderedArea(self.area).values()])

    def test_yields_centerpage_in_addition_to_teaser_when_iterating(self):
        content = zeit.edit.interfaces.IElementReferences(self.cp)
        self.assertEqual([
            u'http://xml.zeit.de/cp_with_teaser',
            u'http://xml.zeit.de/t1',
            u'http://xml.zeit.de/t2',
            u'http://xml.zeit.de/t3'],
            [x.uniqueId for x in content])

    def test_recursivly_referenced_cps_raise_value_error(self):
        cp_with_teaser = self.create_and_checkout_centerpage(
            name='self_referencing_cp')
        zeit.cms.checkout.interfaces.ICheckinManager(cp_with_teaser).checkin()
        area = cp_with_teaser['feature'].create_item('area')
        area.automatic = True
        area.automatic_type = 'centerpage'
        with self.assertRaises(ValueError):
            area.referenced_cp = cp_with_teaser


class HideDupesTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(HideDupesTest, self).setUp()

        t1 = self.create_content('t1', 't1')
        t2 = self.create_content('t2', 't2')
        t3 = self.create_content('t3', 't3')
        cp_with_teaser = self.create_and_checkout_centerpage(
            name='cp_with_teaser', contents=[t1, t2, t3])
        zeit.cms.checkout.interfaces.ICheckinManager(cp_with_teaser).checkin()

        self.cp = self.create_and_checkout_centerpage()
        self.area = self.create_automatic_area(self.cp)
        self.area.referenced_cp = self.repository['cp_with_teaser']

        self.solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)

    def create_automatic_area(self, cp, count=3, type='centerpage'):
        area = cp['feature'].create_item('area')
        area.count = count
        area.automatic_type = type
        area.automatic = True
        return area

    def assertUniqueIds(self, area, *uniqueIds):
        self.assertEqual(
            [list(b)[0].uniqueId for b in IRenderedArea(area).values()],
            ['http://xml.zeit.de' + uid for uid in uniqueIds])

    def test_manual_teaser_already_above_current_area_is_not_shown_again(self):
        self.cp['feature']['lead'].create_item('teaser').append(
            self.repository['t1'])
        self.assertEqual([
            'http://xml.zeit.de/t2',
            'http://xml.zeit.de/t3'
        ], [list(x)[0].uniqueId for x in IRenderedArea(self.area).values()])

    def test_manual_teaser_already_below_current_area_is_not_shown_again(self):
        self.cp['feature'].create_item('area').create_item('teaser').append(
            self.repository['t1'])
        self.assertEqual([
            'http://xml.zeit.de/t2',
            'http://xml.zeit.de/t3'
        ], [list(x)[0].uniqueId for x in IRenderedArea(self.area).values()])

    def test_skipping_duplicate_teaser_retrieves_next_query_result(self):
        self.cp['feature']['lead'].create_item('teaser').append(
            self.repository['t1'])
        self.area.count = 1
        self.assertEqual(
            'http://xml.zeit.de/t2',
            list(IRenderedArea(self.area).values()[0])[0].uniqueId)

    def test_hide_dupes_is_False_then_duplicates_are_not_skipped(self):
        self.cp['feature']['lead'].create_item('teaser').append(
            self.repository['t1'])
        self.area.hide_dupes = False
        self.assertEqual(
            'http://xml.zeit.de/t1',
            list(IRenderedArea(self.area).values()[0])[0].uniqueId)

    def test_already_rendered_area_results_are_cached(self):
        a2 = self.create_automatic_area(self.cp)
        a2.referenced_cp = self.repository['cp_with_teaser']
        a3 = self.create_automatic_area(self.cp)
        a3.referenced_cp = self.repository['cp_with_teaser']

        self.call_count = {}
        real_values = zeit.content.cp.automatic.AutomaticArea.values

        def values_with_count(area):
            self.call_count.setdefault(area.context, 0)
            self.call_count[area.context] += 1
            return real_values(area)

        with mock.patch('zeit.content.cp.automatic.AutomaticArea.values',
                        values_with_count):
            IRenderedArea(a2).values()
            IRenderedArea(a3).values()
        self.assertEqual(1, self.call_count[self.area])

    def test_cp_content_query_filters_duplicates(self):
        lead = self.cp['feature']['lead'].create_item('teaser')
        lead.append(self.repository['t1'])
        lead.append(self.repository['t2'])
        self.assertEqual(
            'http://xml.zeit.de/t3',
            list(IRenderedArea(self.area).values()[0])[0].uniqueId)

    def test_tms_content_query_filters_duplicates(self):
        self.area.automatic_type = 'topicpage'
        self.area.referenced_topicpage = 'mytopic'
        tms = mock.Mock()
        self.zca.patch_utility(tms, zeit.retresco.interfaces.ITMS)
        tms.get_topicpage_documents.return_value = zeit.cms.interfaces.Result([
            {'url': '/t1', 'doc_type': 'testcontenttype'},
            {'url': '/t2', 'doc_type': 'testcontenttype'},
        ])

        lead = self.cp['feature']['lead'].create_item('teaser')
        lead.append(self.repository['t1'])
        self.assertEqual(
            'http://xml.zeit.de/t2',
            list(IRenderedArea(self.area).values()[0])[0].uniqueId)

    def test_tms_content_query_filters_duplicates_tmscontent(self):
        # zeit.web uses a different `_resolve` than vivi, so make sure this
        # still works
        self.area.automatic_type = 'topicpage'
        self.area.referenced_topicpage = 'mytopic'
        tms = mock.Mock()
        self.zca.patch_utility(tms, zeit.retresco.interfaces.ITMS)
        tms.get_topicpage_documents.return_value = zeit.cms.interfaces.Result([
            {'url': '/t1', 'doc_type': 'testcontenttype'},
            {'url': '/t2', 'doc_type': 'testcontenttype'},
        ])

        lead = self.cp['feature']['lead'].create_item('teaser')
        lead.append(self.repository['t1'])

        def resolve_tmscontent(self, doc):
            return zeit.retresco.content.from_tms_representation(doc)

        with mock.patch('zeit.content.cp.automatic.TMSContentQuery._resolve',
                        new=resolve_tmscontent):
            self.assertEqual(
                'http://xml.zeit.de/t2',
                list(IRenderedArea(self.area).values()[0])[0].uniqueId)

    def test_tms_content_query_filters_duplicate_tmscontent_across_areas(self):
        a1 = self.create_automatic_area(self.cp, count=2, type='topicpage')
        a2 = self.create_automatic_area(self.cp, count=3, type='topicpage')
        a3 = self.create_automatic_area(self.cp, count=2, type='topicpage')
        a1.referenced_topicpage = 'tms-id'
        a2.referenced_topicpage = 'tms-id'
        a3.referenced_topicpage = 'tms-id'
        tms = mock.Mock()
        self.zca.patch_utility(tms, zeit.retresco.interfaces.ITMS)
        results = zeit.cms.interfaces.Result()
        for n in range(30):
            url = 'teaser-{}'.format(n)
            self.create_content(url, url)
            results.append(dict(url='/' + url, doc_type='testcontenttype'))
        tms.get_topicpage_documents.return_value = results

        def resolve_tmscontent(self, doc):
            return zeit.retresco.content.from_tms_representation(doc)

        with mock.patch('zeit.content.cp.automatic.TMSContentQuery._resolve',
                        new=resolve_tmscontent):
            self.assertUniqueIds(a1, '/teaser-0', '/teaser-1')
            self.assertUniqueIds(a2, '/teaser-2', '/teaser-3', '/teaser-4')
            self.assertUniqueIds(a3, '/teaser-5', '/teaser-6')

    def test_solr_content_query_filters_duplicates(self):
        self.area.automatic_type = 'query'

        lead = self.cp['feature']['lead'].create_item('teaser')
        lead.append(self.repository['t1'])
        lead.append(self.repository['t2'])

        IRenderedArea(self.area).values()
        self.assertEqual(
            'NOT (uniqueId:"http://xml.zeit.de/t1"'
            ' OR uniqueId:"http://xml.zeit.de/t2")',
            self.solr.search.call_args[1]['fq'])

    def test_elasticsearch_content_query_filters_duplicates(self):
        self.area.automatic_type = 'elasticsearch-query'
        self.area.elasticsearch_raw_query = (
            u'{"query": {"match": {"foo": "äää"}}}')
        elasticsearch = zope.component.getUtility(
            zeit.retresco.interfaces.IElasticsearch)

        lead = self.cp['feature']['lead'].create_item('teaser')
        lead.append(self.repository['t1'])
        lead.append(self.repository['t2'])

        IRenderedArea(self.area).values()

        id1 = zeit.cms.content.interfaces.IUUID(self.repository['t1']).id
        id2 = zeit.cms.content.interfaces.IUUID(self.repository['t2']).id

        self.assertEqual(
            {'query': {'bool': {
                'filter': [
                    {u'match': {u'foo': u'äää'}},
                    {'term': {'payload.workflow.published': True}}],
                'must_not': {'ids': {'values': [id1, id2]}}}}},
            elasticsearch.search.call_args[0][0])

        # since `AutomaticArea.values()` is cached on the transaction boundary
        # now, we'll only see the change with the next request/transaction...
        transaction.commit()

        # Do not filter, if switched off.
        self.area.hide_dupes = False
        IRenderedArea(self.area).values()
        self.assertEqual(
            {'query': {'bool': {'filter': [
                {u'match': {u'foo': u'äää'}},
                {'term': {'payload.workflow.published': True}}]}}},
            elasticsearch.search.call_args[0][0])

    def test_teaser_count(self):
        a1 = self.create_automatic_area(self.cp, count=0, type='topicpage')
        a2 = self.create_automatic_area(self.cp, count=0, type='topicpage')
        a3 = self.create_automatic_area(self.cp, count=2)
        a1.referenced_topicpage = 'tms-id'
        a3.referenced_topicpage = 'tms-id'
        tms_query = zeit.content.cp.automatic.TMSContentQuery(a1)
        self.assertEqual(tms_query._teaser_count, 0)
        a2.count = 3
        self.assertEqual(tms_query._teaser_count, 0)
        a2.referenced_topicpage = 'tms-id'
        self.assertEqual(tms_query._teaser_count, 3)
        a3.automatic_type = 'topicpage'
        self.assertEqual(tms_query._teaser_count, 5)
        a1.count = 7
        self.assertEqual(tms_query._teaser_count, 12)

    def test_total_hits_can_be_called_first(self):
        area = self.create_automatic_area(self.cp)
        area.start = 0          # TODO: are we sure this is _always_ set?
        tms = mock.Mock()
        self.zca.patch_utility(tms, zeit.retresco.interfaces.ITMS)
        results = zeit.cms.interfaces.Result([])
        results.hits = 42
        tms.get_topicpage_documents.return_value = results
        tms_query = zeit.content.cp.automatic.TMSContentQuery(area)
        self.assertEqual(tms_query.total_hits, 42)
