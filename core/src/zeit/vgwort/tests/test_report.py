import time

import pendulum
import transaction
import zope.component
import zope.interface

import zeit.cms.testcontenttype.testcontenttype
import zeit.find.interfaces
import zeit.retresco.interfaces
import zeit.vgwort.interfaces
import zeit.vgwort.report
import zeit.vgwort.testing


class ReportTest(zeit.vgwort.testing.TestCase):
    def setUp(self):
        super().setUp()
        self.vgwort = zope.component.getUtility(zeit.vgwort.interfaces.IMessageService)
        self.content = self.repository['testcontent']

    def tearDown(self):
        self.vgwort.error = False
        super().tearDown()

    def test_source_queries_storage(self):
        # Cannot use vivi APIs to set this up, due to the IPublishInfo mock.
        self.repository.connector.changeProperties(
            self.content.uniqueId,
            {
                ('type', 'http://namespaces.zeit.de/CMS/meta'): 'article',
                ('private_token', 'http://namespaces.zeit.de/CMS/vgwort'): 'token',
                ('date_first_released', 'http://namespaces.zeit.de/CMS/document'): pendulum.now(
                    'UTC'
                )
                .subtract(days=8)
                .isoformat(),
            },
        )
        transaction.commit()

        source = zope.component.getUtility(zeit.vgwort.interfaces.IReportableContentSource)
        self.assertEqual([self.content.uniqueId], [x.uniqueId for x in source])

    def test_successful_report_should_mark_content(self):
        now = pendulum.now('UTC')
        time.sleep(0.25)
        zeit.vgwort.report.report(self.content)
        transaction.commit()
        self.assertEqual([self.content], self.vgwort.calls)
        info = zeit.vgwort.interfaces.IReportInfo(self.content)
        self.assertEqual(None, info.reported_error)
        self.assertTrue(info.reported_on > now)

    def test_semantic_error_should_mark_content(self):
        self.vgwort.error = zeit.vgwort.interfaces.WebServiceError
        zeit.vgwort.report.report(self.content)
        transaction.commit()
        info = zeit.vgwort.interfaces.IReportInfo(self.content)
        self.assertEqual('Provoked error', info.reported_error)
        self.assertEqual(None, info.reported_on)

    def test_technical_error_should_not_mark_content(self):
        self.vgwort.error = zeit.vgwort.interfaces.TechnicalError
        zeit.vgwort.report.report(self.content)
        transaction.commit()
        info = zeit.vgwort.interfaces.IReportInfo(self.content)
        self.assertEqual(None, info.reported_error)
        self.assertEqual(None, info.reported_on)
