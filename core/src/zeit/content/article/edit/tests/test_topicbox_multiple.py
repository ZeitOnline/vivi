import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.edit.interfaces
from zeit.content.article.edit.topicbox_multiple import TopicboxMultiple


class TestTopicboxMultiple(zeit.content.article.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.MOCK_LAYER

    def get_topicbox_multiple(self):
        import lxml.objectify
        box = TopicboxMultiple(None, lxml.objectify.E.topicbox_multiple())
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

    def test_topicbox_multiple_reference(self):
        box = self.get_topicbox_multiple()
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        box.first_reference = article
        self.assertEqual([article, None, None, ], box.values)

    def test_topicbox_multiple_source_elasticsearch(self):
        box = self.get_topicbox_multiple()
        box.source_type = 'elasticsearch-query'
        box.elasticsearch_raw_query = '{}'
        box.source = True
        self.assertEqual('http://xml.zeit.de/politik/ausland/2020-10/'
                         'coronavirus-weltweit-covid-19-pandemie-'
                         'neuinfektionen-entwicklung-liveblog',
                         box.first_reference.uniqueId)
        self.assertEqual('http://xml.zeit.de/politik/deutschland/2021-01/'
                         'bundeswehr-annegret-kramp-karrenbauer-drohne-'
                         'luftverteidigung',
                         box.second_reference.uniqueId)
        self.assertEqual('http://xml.zeit.de/wissen/gesundheit/2021-01/'
                         'coronavirus-neuinfektionen-rki-gesundheitsaemter-'
                         'deutschland-todesfaelle-sachsen',
                         box.third_reference.uniqueId)

    def test_topicbox_multiple_source_custom(self):
        box = self.get_topicbox_multiple()
        box.source_type = 'custom'
        box.query = (('ressort', 'eq', 'Politik', 'Partnerschaft'),)
        box.source = True
        self.assertEqual('http://xml.zeit.de/politik/ausland/2020-10/'
                         'coronavirus-weltweit-covid-19-pandemie-'
                         'neuinfektionen-entwicklung-liveblog',
                         box.first_reference.uniqueId)
        self.assertEqual('http://xml.zeit.de/politik/deutschland/2021-01/'
                         'bundeswehr-annegret-kramp-karrenbauer-drohne-'
                         'luftverteidigung',
                         box.second_reference.uniqueId)
        self.assertEqual('http://xml.zeit.de/wissen/gesundheit/2021-01/'
                         'coronavirus-neuinfektionen-rki-gesundheitsaemter-'
                         'deutschland-todesfaelle-sachsen',
                         box.third_reference.uniqueId)

    def test_topicbox_multiple_topicpage(self):
        box = self.get_topicbox_multiple()
        box.source_type = 'topicpage'
        box.topicpage = 'angela-merkel'
        box.source = True
        self.assertEqual('http://xml.zeit.de/politik/ausland/2020-10/'
                         'coronavirus-weltweit-covid-19-pandemie-'
                         'neuinfektionen-entwicklung-liveblog',
                         box.first_reference.uniqueId)
        self.assertEqual('http://xml.zeit.de/politik/deutschland/2021-01/'
                         'bundeswehr-annegret-kramp-karrenbauer-drohne-'
                         'luftverteidigung',
                         box.second_reference.uniqueId)
        self.assertEqual('http://xml.zeit.de/wissen/gesundheit/2021-01/'
                         'coronavirus-neuinfektionen-rki-gesundheitsaemter-'
                         'deutschland-todesfaelle-sachsen',
                         box.third_reference.uniqueId)
