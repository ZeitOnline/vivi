from zeit.contentquery.interfaces import QueryTypeSource
from zeit.contentquery.query import CustomContentQuery
import zeit.cms.testing


class QueryTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_conditions_retrieve_identifier_from_descriptor(self):
        for name in QueryTypeSource():
            with self.assertNothingRaised():
                CustomContentQuery._fieldname(name)
