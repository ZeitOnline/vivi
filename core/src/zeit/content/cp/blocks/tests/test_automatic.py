from zeit.cms.testcontenttype.testcontenttype import TestContentType
from zeit.content.cp.interfaces import IRenderedArea
import mock
import transaction
import zeit.content.cp.testing


class AutomaticTeaserBlockTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticTeaserBlockTest, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()

    def test_materialize_creates_normal_teaser_block(self):
        self.repository['t1'] = TestContentType()
        self.repository['t2'] = TestContentType()

        lead = self.repository['cp']['lead']
        lead.count = 3
        lead.automatic = True
        lead.automatic_type = 'query'

        with mock.patch('zeit.find.search.search') as search:
            search.side_effect = [[dict(uniqueId='http://xml.zeit.de/t1'),
                                   dict(uniqueId='http://xml.zeit.de/t2')]]
            lead.values()[0].materialize()

        transaction.commit()  # Clear teaser present above/below caches.
        with mock.patch('zeit.find.search.search') as search:
            search.side_effect = [
                [dict(uniqueId='http://xml.zeit.de/t1'),
                 dict(uniqueId='http://xml.zeit.de/t2')],
                [],
            ]
            result = IRenderedArea(lead).values()

        self.assertEqual(['teaser', 'auto-teaser'], [x.type for x in result])
        self.assertEqual(
            ['http://xml.zeit.de/t1',
             'http://xml.zeit.de/t2'], [list(x)[0].uniqueId for x in result])
