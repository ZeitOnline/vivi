import zope.component

import zeit.newsimport.interfaces
import zeit.newsimport.testing


class TestApiRepsonse(zeit.newsimport.testing.FunctionalAPITestCase):
    def test_get_queue_entries(self):
        dpa = zope.component.getUtility(zeit.newsimport.interfaces.IDPA, name='weblines')
        entries = dpa.get_entries()
        self.assertTrue(self.layer['dpa_api_get'].called)
        self.assertEqual('dpa', entries[0]['creditline'])
        self.assertEqual(35, len(entries[0]))

    def test_delete_entry_from_queue(self):
        receipt = 'AQEB93'
        dpa = zope.component.getUtility(zeit.newsimport.interfaces.IDPA, name='weblines')
        dpa.delete_entry(receipt)
        self.assertTrue(self.layer['dpa_api_delete'].called)
