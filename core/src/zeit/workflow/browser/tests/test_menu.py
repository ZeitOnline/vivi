import zope.testbrowser.browser

import zeit.workflow.testing


class WorkflowTabTest(zeit.workflow.testing.BrowserTestCase):
    def test_workflow_tab_is_shown_for_repository_content(self):
        b = self.browser
        b.open('/repository/testcontent')
        with self.assertNothingRaised():
            b.getLink('Workflow')

    def test_workflow_tab_is_not_shown_for_local_content(self):
        b = self.browser
        b.open('/repository/testcontent')
        b.getLink('Checkout').click()
        with self.assertRaises(zope.testbrowser.browser.LinkNotFoundError):
            b.getLink('Workflow')
