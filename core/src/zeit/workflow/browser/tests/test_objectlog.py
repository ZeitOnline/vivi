from pendulum import datetime
import time_machine

import zeit.objectlog.interfaces
import zeit.workflow.testing


class ObjectLog(zeit.workflow.testing.BrowserTestCase):
    def test_log_entries_are_grouped_by_date(self):
        testcontent = self.repository['testcontent']
        object_log = zeit.objectlog.interfaces.ILog(testcontent)
        with time_machine.travel(datetime(2012, 6, 12, 9, 14)):
            object_log.log('one')
        with time_machine.travel(datetime(2012, 6, 12, 10, 25)):
            object_log.log('two')
        with time_machine.travel(datetime(2012, 6, 13, 12, 8)):
            object_log.log('three')
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
