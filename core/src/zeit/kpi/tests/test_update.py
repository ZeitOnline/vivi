from sqlalchemy import select
import transaction
import zope.component

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.connector.models import Content
import zeit.cms.testing
import zeit.connector.interfaces
import zeit.kpi.interfaces
import zeit.kpi.testing
import zeit.kpi.update


class UpdateTest(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.kpi.testing.ZOPE_LAYER

    def test_paginates_through_sql_result(self):
        for i in range(15):
            self.repository[f'testcontent-{i}'] = ExampleContentType()
        transaction.commit()

        zeit.kpi.update.update(select(Content), kpi_batch_size=10, sql_batch_size=2)
        source = zope.component.getUtility(zeit.kpi.interfaces.IKPIDatasource)
        self.assertEqual(2, len(source.calls))
