import mechanize
import zeit.cms.testing
import zeit.workflow.testing


class WorkflowTabTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.workflow.testing.WorkflowLayer

    def test_workflow_tab_is_shown_for_repository_content(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/Somalia')
        with self.assertNothingRaised():
            b.getLink('Workflow')

    def test_workflow_tab_is_not_shown_for_local_content(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/Somalia')
        b.getLink('Checkout').click()
        with self.assertRaises(mechanize.LinkNotFoundError):
            b.getLink('Workflow')
