# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import datetime
import zeit.cms.testing
import zeit.objectlog.interfaces
import zeit.workflow.testing


class ObjectLog(zeit.cms.testing.BrowserTestCase):

    layer = zeit.workflow.testing.WorkflowLayer

    def test_log_entries_are_grouped_by_date(self):
        testcontent = self.repository['testcontent']
        object_log = zeit.objectlog.interfaces.ILog(testcontent)
        with zeit.cms.testing.interaction():
            with zeit.cms.testing.site(self.getRootFolder()):
                object_log.log('one', timestamp=datetime(2012, 6, 12, 9, 14))
                object_log.log('two', timestamp=datetime(2012, 6, 12, 10, 25))
                object_log.log('three', timestamp=datetime(2012, 6, 13, 12, 8))
        self.browser.handleErrors = False
        self.browser.open(
            'http://localhost/++skin++vivi/repository/testcontent/@@objectlog')
        self.assertEllipsis("""...
            <th colspan="3">13.06.2012</th>...
            <td>three</td>
            <td>12:08</td>
            <td class="principal">Zope.User</td>...
            <th colspan="3">12.06.2012</th>...
            <td>two</td>
            <td>10:25</td>
            <td class="principal">Zope.User</td>...
            <td>one</td>
            <td>09:14</td>
            <td class="principal">Zope.User</td>...
            """, self.browser.contents)
