from datetime import datetime
import pytz
import zeit.objectlog.interfaces
import zeit.workflow.testing


class ObjectLog(zeit.workflow.testing.BrowserTestCase):
    def test_log_entries_are_grouped_by_date(self):
        testcontent = self.repository['testcontent']
        object_log = zeit.objectlog.interfaces.ILog(testcontent)
        object_log.log('one', timestamp=datetime(2012, 6, 12, 9, 14, tzinfo=pytz.UTC))
        object_log.log('two', timestamp=datetime(2012, 6, 12, 10, 25, tzinfo=pytz.UTC))
        object_log.log('three', timestamp=datetime(2012, 6, 13, 12, 8, tzinfo=pytz.UTC))
        self.browser.open('http://localhost/++skin++vivi/repository/testcontent/@@objectlog')
        self.assertEllipsis(
            """...
            <th colspan="3">13.06.2012</th>...
            <td>three</td>
            <td>14:08</td>
            <td class="principal">User</td>...
            <th colspan="3">12.06.2012</th>...
            <td>two</td>
            <td>12:25</td>
            <td class="principal">User</td>...
            <td>one</td>
            <td>11:14</td>
            <td class="principal">User</td>...
            """,
            self.browser.contents,
        )
