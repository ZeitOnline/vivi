import mock
import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.content.video.video
import zeit.edit.interfaces
import zope.component
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType


class TestTopicbox(zeit.content.article.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.MOCK_LAYER

    def setUp(self):
        super().setUp()
        self.repository['art1'] = zeit.content.article.article.Article()
        self.repository['art2'] = zeit.content.article.article.Article()
        self.repository['art3'] = zeit.content.article.article.Article()
        self.repository['video'] = zeit.content.video.video.Video()
        self.elastic = zope.component.getUtility(
            zeit.retresco.interfaces.IElasticsearch)
        self.tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = zeit.cms.interfaces.Result([
            {'url': '/art1'},
            {'url': '/video'},
            {'url': '/art2'},
            {'url': '/art3'}])
        result.hits = 4
        self.elastic.search.return_value = result
        self.tms.get_topicpage_documents.return_value = result

    def get_topicbox(self):
        from zeit.content.article.edit.topicbox import Topicbox
        import lxml.objectify
        box = Topicbox(None, lxml.objectify.E.topicbox())
        self.repository['art'] = zeit.content.article.article.Article()
        box.__parent__ = self.repository['art']
        return box

    def get_cp(self, content=None):
        import zeit.content.cp.centerpage
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        if content:
            region = self.repository['cp'].create_item('region')
            area = region.create_item('area')
            for cont in content:
                teaser = area.create_item('teaser')
                teaser.insert(0, cont)
        return self.repository['cp']

    def test_topicbox_values_does_not_contain_empty_reference(self):
        box = self.get_topicbox()
        box.automatic_type = 'manual'
        article = zeit.cms.interfaces.ICMSContent(
            "http://xml.zeit.de/online/2007/01/Somalia")
        box.first_reference = article
        self.assertEqual([article, ], box.values())

    def test_empty_referenced_cp_has_no_values(self):
        box = self.get_topicbox()
        cp = self.get_cp()
        box.first_reference = cp
        box.automatic_type = 'manual'
        self.assertEqual(cp, box.referenced_cp)
        self.assertEqual([], box.values())

    def test_topicbox_parent_is_excluded_if_in_cp(self):
        self.repository['foo'] = ExampleContentType()
        box = self.get_topicbox()
        box.automatic_type = 'manual'
        art = zeit.content.article.interfaces.IArticle(box)
        cp = self.get_cp(content=[self.repository['foo'], art])
        box.first_reference = cp
        self.assertEqual([self.repository['foo'], ], box.values())

    def test_box_uses_cp_content(self):
        box = self.get_topicbox()
        box.automatic_type = 'manual'
        article = zeit.cms.interfaces.ICMSContent(
            "http://xml.zeit.de/online/2007/01/Somalia")
        cp = self.get_cp(content=[article, ])
        box.first_reference = cp
        self.assertEqual([article], box.values())

    def test_box_uses_first_three_cp_entries(self):
        content = []
        article_names = ['foo', 'bar', 'baz', 'qux']
        for name in article_names:
            self.repository[name] = ExampleContentType()
            content.append(self.repository[name])
        box = self.get_topicbox()
        box.automatic_type = 'manual'
        cp = self.get_cp(content=content)
        box.first_reference = cp
        self.assertEqual(cp, box.referenced_cp)
        self.assertEqual(content[:3], box.values())

    def test_box_if_cp_is_referenced_rest_is_ignored(self):
        self.repository['foo'] = ExampleContentType()
        box = self.get_topicbox()
        box.automatic_type = 'manual'
        cp = self.get_cp(content=[self.repository['foo']])
        box.first_reference = cp
        box.second_reference = zeit.cms.interfaces.ICMSContent(
            "http://xml.zeit.de/online/2007/01/Somalia")
        self.assertEqual([self.repository['foo'], ], box.values())

    def test_topicbox_defaults_to_automatic_type_centerpage(self):
        box = self.get_topicbox()
        self.assertEqual('centerpage', box.automatic_type)

    def test_topicbox_source_centerpage(self):
        box = self.get_topicbox()
        box.referenced_cp = self.get_cp(content=[
            self.repository['art1'],
            self.repository['art2'],
            self.repository['art3'], ])
        values = box.values()
        self.assertEqual('http://xml.zeit.de/art1', values[0].uniqueId)
        self.assertEqual('http://xml.zeit.de/art2', values[1].uniqueId)
        self.assertEqual('http://xml.zeit.de/art3', values[2].uniqueId)

    def test_topicbox_source_elasticsearch(self):
        box = self.get_topicbox()
        box.automatic_type = 'elasticsearch-query'
        box.elasticsearch_raw_query = '{}'
        values = box.values()
        self.assertEqual('http://xml.zeit.de/art1', values[0].uniqueId)
        self.assertEqual('http://xml.zeit.de/video', values[1].uniqueId)
        self.assertEqual('http://xml.zeit.de/art2', values[2].uniqueId)

    def test_topicbox_source_topicpage(self):
        box = self.get_topicbox()
        box.automatic_type = 'topicpage'
        box.referenced_topicpage = 'angela-merkel'
        values = box.values()
        self.assertEqual('http://xml.zeit.de/art1', values[0].uniqueId)
        self.assertEqual('http://xml.zeit.de/video', values[1].uniqueId)
        self.assertEqual('http://xml.zeit.de/art2', values[2].uniqueId)

    def test_topicbox_source_preconfigured_query_complete_query(self):
        box = self.get_topicbox()
        box.automatic_type = 'preconfigured-query'
        box.preconfigured_query = 'esquery1'
        contentquery = zope.component.getAdapter(
            box,
            zeit.contentquery.interfaces.IContentQuery,
            name=box.automatic_type)
        query = contentquery.query
        values = box.values()
        self.assertEqual(
            {'query': {'query': {'term': {'doc_type': 'TESTTYPE'}}}}, query)
        self.assertEqual('http://xml.zeit.de/art1', values[0].uniqueId)
        self.assertEqual('http://xml.zeit.de/video', values[1].uniqueId)
        self.assertEqual('http://xml.zeit.de/art2', values[2].uniqueId)

    def test_topicbox_source_preconfigured_query_not_complete_query(self):
        box = self.get_topicbox()
        box.automatic_type = 'preconfigured-query'
        box.preconfigured_query = 'esquery2'
        contentquery = zope.component.getAdapter(
            box,
            zeit.contentquery.interfaces.IContentQuery,
            name=box.automatic_type)
        query = contentquery.query
        values = box.values()
        self.assertEqual({'query': {'term': {'doc_type': 'TESTTYPE2'}}}, query)
        self.assertEqual('http://xml.zeit.de/art1', values[0].uniqueId)
        self.assertEqual('http://xml.zeit.de/video', values[1].uniqueId)
        self.assertEqual('http://xml.zeit.de/art2', values[2].uniqueId)

    def test_topicbox_source_related_api_should_return_result(self):
        box = self.get_topicbox()
        box.automatic_type = 'related-api'
        contentquery = zope.component.getAdapter(
            box,
            zeit.contentquery.interfaces.IContentQuery,
            name=box.automatic_type)

        result, hits = contentquery._get_documents(0, 3)

        self.assertEqual(
            list(result), [{'article1'}, {'article2'}, {'article3'}])
        self.assertEqual(hits, 3)

    def test_topicbox_values_deduplication(self):
        box = self.get_topicbox()
        box.referenced_cp = self.get_cp(content=[
            self.repository['art1'],
            self.repository['art2'],
            self.repository['art2'],
            self.repository['art3'], ])
        values = box.values()
        self.assertEqual('http://xml.zeit.de/art1', values[0].uniqueId)
        self.assertEqual('http://xml.zeit.de/art2', values[1].uniqueId)
        self.assertEqual('http://xml.zeit.de/art3', values[2].uniqueId)
