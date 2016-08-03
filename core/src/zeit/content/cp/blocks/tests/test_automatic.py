from zeit.cms.testcontenttype.testcontenttype import TestContentType
from zeit.content.cp.interfaces import IRenderedArea
import zeit.content.cp.testing
import zeit.solr.interfaces
import zope.component


class AutomaticTeaserBlockTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticTeaserBlockTest, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)

    def test_materialize_creates_normal_teaser_block(self):
        self.repository['t1'] = TestContentType()
        self.repository['t2'] = TestContentType()

        lead = self.repository['cp']['lead']
        lead.count = 2
        lead.automatic = True
        lead.automatic_type = 'query'

        self.solr.search.return_value = [
            dict(uniqueId='http://xml.zeit.de/t1'),
            dict(uniqueId='http://xml.zeit.de/t2')]
        lead.values()[0].materialize()

        result = IRenderedArea(lead).values()
        self.assertEqual(['teaser', 'auto-teaser'], [x.type for x in result])
