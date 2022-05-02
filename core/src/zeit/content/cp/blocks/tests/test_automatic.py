from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.content.cp.interfaces import IRenderedArea
import transaction
import zeit.content.cp.testing
import zeit.retresco.interfaces
import zope.component


class AutomaticTeaserBlockTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticTeaserBlockTest, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.elastic = zope.component.getUtility(
            zeit.retresco.interfaces.IElasticsearch)

    def test_materialize_creates_normal_teaser_block(self):
        self.repository['t1'] = ExampleContentType()
        self.repository['t2'] = ExampleContentType()

        lead = self.repository['cp']['lead']
        lead.count = 2
        lead.automatic = True
        lead.automatic_type = 'query'

        self.elastic.search.return_value = zeit.cms.interfaces.Result(
            [{'url': '/t1'}, {'url': '/t2'}])
        self.elastic.search.return_value.hits = 2
        lead.values()[0].materialize()

        # since `AutomaticArea.values()` is cached on the transaction boundary
        # now, we'll only see the change with the next request/transaction...
        transaction.commit()

        result = IRenderedArea(lead).values()
        self.assertEqual(['teaser', 'auto-teaser'], [x.type for x in result])

    def test_automatic_teaser_block_uses_first_default_teaser_definition(self):
        """There are two defaults defined for the duo are in layout.xml and the
         first one should be used"""
        self.repository['t1'] = ExampleContentType()
        cp = self.repository['cp']
        duo_region = cp['feature'].create_item('area')
        duo_region.kind = 'duo'
        duo_region.count = 1
        duo_region.automatic = True
        duo_region.automatic_type = 'query'

        self.elastic.search.return_value = zeit.cms.interfaces.Result(
            [{'url': '/t1'}])
        self.elastic.search.return_value.hits = 1
        teaser = duo_region.values()[0]
        self.assertEqual('two-side-by-side', teaser.layout.id)

    def test_automatic_teaser_block_should_not_force_mobile_image(self):
        self.repository['t1'] = ExampleContentType()
        cp = self.repository['cp']
        region = cp['feature'].create_item('area')
        region.kind = 'major'
        region.count = 1
        region.automatic = True
        region.automatic_type = 'query'

        self.elastic.search.return_value = zeit.cms.interfaces.Result(
            [{'url': '/t1'}])
        self.elastic.search.return_value.hits = 1
        teaser = region.values()[0]
        self.assertFalse(teaser.force_mobile_image)
