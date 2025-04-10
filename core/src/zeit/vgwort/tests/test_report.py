import time

from sqlalchemy import select
import pendulum
import transaction
import zope.component
import zope.interface

from zeit.cms.interfaces import DOCUMENT_SCHEMA_NS
from zeit.connector.models import Content
import zeit.cms.testcontenttype.testcontenttype
import zeit.find.interfaces
import zeit.retresco.interfaces
import zeit.vgwort.interfaces
import zeit.vgwort.report
import zeit.vgwort.testing


class ReportTest(zeit.vgwort.testing.SQLTestCase):
    def setUp(self):
        super().setUp()
        self.vgwort = zope.component.getUtility(zeit.vgwort.interfaces.IMessageService)

    def tearDown(self):
        self.vgwort.error = False
        super().tearDown()

    def test_source_queries_storage(self):
        release_date = pendulum.now('UTC').subtract(days=8).isoformat()
        res = self.add_resource(
            'testcontent',
            type='article',
            properties={
                ('date_first_released', f'{DOCUMENT_SCHEMA_NS}'): release_date,
                ('private_token', 'http://namespaces.zeit.de/CMS/vgwort'): 'token',
                ('reported_error', 'http://namespaces.zeit.de/CMS/vgwort'): '',
                ('reported_on', 'http://namespaces.zeit.de/CMS/vgwort'): '',
            },
        )
        query = select(Content).filter_by(type='article')
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        result = repository.search(query)

        source = zope.component.getUtility(zeit.vgwort.interfaces.IReportableContentSource)
        result = list(source)
        self.assertEqual(len(result), 1)
        self.assertEqual(res.id, result[0].uniqueId)

    def test_successful_report_should_mark_content(self):
        now = pendulum.now('UTC')
        time.sleep(0.25)
        self.add_resource('testcontent')
        content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testing/testcontent')
        zeit.vgwort.report.report(content)
        transaction.commit()
        self.assertEqual([content], self.vgwort.calls)
        info = zeit.vgwort.interfaces.IReportInfo(content)
        self.assertEqual(None, info.reported_error)
        self.assertTrue(info.reported_on > now)

    def test_semantic_error_should_mark_content(self):
        self.vgwort.error = zeit.vgwort.interfaces.WebServiceError
        self.add_resource('testcontent')
        content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testing/testcontent')
        zeit.vgwort.report.report(content)
        transaction.commit()
        info = zeit.vgwort.interfaces.IReportInfo(content)
        self.assertEqual('Provoked error', info.reported_error)
        self.assertEqual(None, info.reported_on)

    def test_technical_error_should_not_mark_content(self):
        self.vgwort.error = zeit.vgwort.interfaces.TechnicalError
        self.add_resource('testcontent')
        content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testing/testcontent')
        zeit.vgwort.report.report(content)
        transaction.commit()
        info = zeit.vgwort.interfaces.IReportInfo(content)
        self.assertEqual(None, info.reported_error)
        self.assertEqual(None, info.reported_on)
