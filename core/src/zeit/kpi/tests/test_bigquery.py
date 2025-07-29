import zope.component

import zeit.kpi.interfaces
import zeit.kpi.testing


class BigQueryTest(zeit.cms.testing.FunctionalTestCase):
    layer = zeit.kpi.testing.BIGQUERY_LAYER

    def test_query_according_url(self):
        api = zope.component.getUtility(zeit.kpi.interfaces.IKPIDatasource)
        data = api.query([self.repository['testcontent']])
        self.assertEqual(1, len(data))
        self.assertEqual(self.repository['testcontent'], data[0][0])
        kpi = data[0][1]
        self.assertEqual(kpi.visits, 1)
        self.assertEqual(kpi.comments, 2)
        self.assertEqual(kpi.subscriptions, 3)
