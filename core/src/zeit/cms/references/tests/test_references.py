from sqlalchemy import select
import sqlalchemy.orm
import transaction
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import IUUID
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.connector.models import Reference
import zeit.cms.testing


class ExtractReferencesTest(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        FEATURE_TOGGLES.set('store_references')

        # Maybe just implementing IExtractReferences for IRelatedContent
        # would be easier than doing this dance to pretend we have authors?
        registry = zope.component.getGlobalSiteManager()
        registry.registerAdapter(zeit.cms.related.related.BasicReference, name='author')
        registry.registerAdapter(zeit.cms.related.related.RelatedReference, name='author')

    def test_stores_references_on_checkin(self):
        article = self.repository['testcontent']
        self.repository['author'] = ExampleContentType()
        transaction.commit()
        author = self.repository['author']

        with checked_out(article) as co:
            co.authorships = (co.authorships.create(author),)
        transaction.commit()

        columns = [c.key for c in sqlalchemy.orm.class_mapper(Reference).columns if c.primary_key]
        result = self.repository.connector.session.execute(select(Reference)).scalars()
        references = [{c: getattr(x, c) for c in columns} for x in result]
        self.assertEqual(
            [
                {
                    'source': IUUID(article).shortened,
                    'target': IUUID(author).shortened,
                    'type': 'author',
                }
            ],
            references,
        )
