# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from StringIO import StringIO
import csv
import zeit.vgwort.interfaces
import zeit.vgwort.report
import zeit.vgwort.testing
import zope.security.management
import zope.testbrowser.testing


class ReportOverviewTest(zeit.vgwort.testing.TestCase):

    def setUp(self):
        super(ReportOverviewTest, self).setUp()
        zope.security.management.endInteraction()


    def test_smoke_download_csv(self):
        # can't really test query results since the mock connector search
        # result is static
        browser = zope.testbrowser.testing.Browser()
        browser.addHeader('Authorization', 'Basic user:userpw')
        browser.handleErrors = False
        browser.open(
            'http://localhost/++skin++vivi/@@zeit.vgwort.report_status')
        report = csv.DictReader(StringIO(browser.contents), delimiter=';')
        row = report.next()
        self.assertEquals('http://xml.zeit.de/online/2007/01/Somalia',
                          row['uniqueId'])
