# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import TestContentType
import zeit.cms.testing


class MultiResourceTest(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(MultiResourceTest, self).setUp()
        # We use TestContentType as reference targets in the tests below. Since
        # those implement ICommonMetadata, its XMLReferenceUpdater will write
        # 'title' (among others) into the XML here.
        TestContentType.references = zeit.cms.content.property.MultiResource(
            '.body.references.reference', 'related')

    def tearDown(self):
        del TestContentType.references
        super(MultiResourceTest, self).tearDown()

    def test_should_be_updated_on_checkin(self):
        target = TestContentType()
        target.teaserTitle = u'foo'
        self.repository['target'] = target

        content = TestContentType()
        content.references = (self.repository['target'],)
        self.repository['content'] = content

        with checked_out(self.repository['target']) as co:
            co.teaserTitle = u'bar'
        with checked_out(self.repository['content']):
            pass

        body = self.repository['content'].xml['body']
        self.assertEqual(
            u'bar', body['references']['reference']['title'])
