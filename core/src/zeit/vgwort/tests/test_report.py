from unittest import mock
import datetime
import pytz
import time
import zeit.cms.testcontenttype.testcontenttype
import zeit.find.interfaces
import zeit.retresco.interfaces
import zeit.vgwort.interfaces
import zeit.vgwort.report
import zeit.vgwort.testing
import zope.component
import zope.interface


class ReportTest(zeit.vgwort.testing.TestCase):

    def setUp(self):
        super().setUp()
        self.vgwort = zope.component.getUtility(
            zeit.vgwort.interfaces.IMessageService)
        self.tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)

    def tearDown(self):
        self.vgwort.error = False
        super().tearDown()

    def test_source_queries_elastic(self):
        elastic = mock.Mock()
        zope.component.getGlobalSiteManager().registerUtility(
            elastic, zeit.find.interfaces.ICMSSearch)
        elastic.search.return_value = zeit.cms.interfaces.Result(
            [{'url': '/testcontent'}])
        source = zope.component.getUtility(
            zeit.vgwort.interfaces.IReportableContentSource)
        result = list(source)
        self.assertEqual([self.repository['testcontent']], result)

    def test_successful_report_should_mark_content(self):
        now = datetime.datetime.now(pytz.UTC)
        time.sleep(0.25)
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        zeit.vgwort.report.report(content)
        self.assertEqual([content], self.vgwort.calls)
        info = zeit.vgwort.interfaces.IReportInfo(content)
        self.assertEqual(None, info.reported_error)
        self.assertTrue(info.reported_on > now)
        self.assertTrue(self.tms.index.called)

    def test_semantic_error_should_mark_content(self):
        self.vgwort.error = zeit.vgwort.interfaces.WebServiceError

        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        zeit.vgwort.report.report(content)

        info = zeit.vgwort.interfaces.IReportInfo(content)
        self.assertEqual('Provoked error', info.reported_error)
        self.assertEqual(None, info.reported_on)
        self.assertTrue(self.tms.index.called)

    def test_technical_error_should_not_mark_content(self):
        self.vgwort.error = zeit.vgwort.interfaces.TechnicalError

        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        zeit.vgwort.report.report(content)

        info = zeit.vgwort.interfaces.IReportInfo(content)
        self.assertEqual(None, info.reported_error)
        self.assertEqual(None, info.reported_on)
        self.assertFalse(self.tms.index.called)
