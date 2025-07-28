from sqlalchemy import select
import zope.component

from zeit.connector.models import Content
import zeit.cms.testing
import zeit.connector.interfaces
import zeit.kpi.interfaces
import zeit.kpi.testing
import zeit.kpi.update


class UpdateTest(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.kpi.testing.ZOPE_LAYER

    def test_paginates_through_sql_result(self):
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        connector.search_result_count = 15
        connector.search_result = ['http://xml.zeit.de/testcontent'] * 2

        zeit.kpi.update.update(select(Content), kpi_batch_size=10, sql_batch_size=2)
        source = zope.component.getUtility(zeit.kpi.interfaces.IKPIDatasource)
        self.assertEqual(2, len(source.calls))
        self.assertIn('LIMIT 2 OFFSET 4', connector.search_args[2])
