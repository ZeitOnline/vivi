# coding: utf-8
import zeit.cms.testing
import zope.component


class GoogleNewsTopics(zeit.cms.testing.ZeitCmsTestCase):

    @property
    def topics(self):
        return zope.component.getUtility(
            zeit.cms.tagging.interfaces.ICurrentTopics)

    def test_parses_response_into_data_dict(self):
        self.assertEqual(
            u'Aaa Test', self.topics('Wirtschaft')[0])

    def test_sorts_results_alphabetically_upper_before_lower(self):
        self.assertEqual(
            u'Aaa Test', self.topics('Wirtschaft')[0])
        self.assertEqual(
            u'andreas breitner', self.topics('Wirtschaft')[1])

    def test_headlines_are_not_keywords(self):
        self.assertIn(u'FC Liverpool', self.topics.headlines)
        self.assertNotIn(u'FC Liverpool', self.topics())

    def test_no_ressort_given_returns_all_keywords(self):
        self.assertEqual(u'Europäisches Parlament', self.topics()[0])

    def test_unknown_ressort_returns_empty_list(self):
        self.assertEqual([], self.topics('Unknown'))

    def test_ressorts_are_mapped_to_categories(self):
        self.assertIn('YouTube', self.topics('Mobilitaet'))
