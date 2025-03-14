from pendulum import datetime

import zeit.cms.workflow.interfaces
import zeit.vgwort.interfaces
import zeit.vgwort.testing


class RetryReport(zeit.vgwort.testing.BrowserTestCase):
    login_as = 'producer:producerpw'

    def test_resets_report_properties(self):
        content = self.repository['testcontent']
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_on = datetime(2017, 5, 22)
        zeit.cms.workflow.interfaces.IPublishInfo(content).date_first_released = info.reported_on

        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent/@@vgwort.html')
        self.assertEllipsis('...Meldung erfolgreich...', b.contents)
        b.getControl('Erneut melden').click()
        self.assertEllipsis('...Nicht gemeldet...', b.contents)
