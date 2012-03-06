# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import pytz
import zeit.cms.testcontenttype.testcontenttype
import zeit.vgwort.interfaces
import zeit.vgwort.report
import zeit.vgwort.testing
import zope.component
import zope.interface


class ReportTest(zeit.vgwort.testing.TestCase):

    def setUp(self):
        super(ReportTest, self).setUp()
        self.vgwort = zope.component.getUtility(
            zeit.vgwort.interfaces.IMessageService)

    def tearDown(self):
        self.vgwort.error = False
        super(ReportTest, self).tearDown()

    def test_source_smoke(self):
        source = zope.component.getUtility(
            zeit.vgwort.interfaces.IReportableContentSource)
        result = list(source)
        self.assertEqual(3, len(result))

    def test_successful_report_should_mark_content(self):
        now = datetime.datetime.now(pytz.UTC)
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        zeit.vgwort.report.report(content)
        self.assertEqual([content], self.vgwort.calls)
        info = zeit.vgwort.interfaces.IReportInfo(content)
        self.assertEqual(None, info.reported_error)
        self.assertTrue(info.reported_on > now)

    def test_semantic_error_should_mark_content(self):
        self.vgwort.error = zeit.vgwort.interfaces.WebServiceError

        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        zeit.vgwort.report.report(content)

        info = zeit.vgwort.interfaces.IReportInfo(content)
        self.assertEqual('Provoked error', info.reported_error)
        self.assertEqual(None, info.reported_on)

    def test_technical_error_should_not_mark_content(self):
        self.vgwort.error = zeit.vgwort.interfaces.TechnicalError

        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        zeit.vgwort.report.report(content)

        info = zeit.vgwort.interfaces.IReportInfo(content)
        self.assertEqual(None, info.reported_error)
        self.assertEqual(None, info.reported_on)
