import zope.component.hooks

from zeit.cms.checkout.helper import checked_out
import zeit.cms.content.interfaces
import zeit.workflow.testing


class WorkflowFormTest(zeit.workflow.testing.BrowserTestCase):
    def test_publish_content(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent' '/@@workflow.html')
        b.getControl('Urgent').click()
        b.getControl('Save state and publish now').click()
        self.assertEllipsis('...Publication scheduled...', b.contents)
        zeit.workflow.testing.run_tasks()

    def test_updates_last_semantic_change_via_checkbox(self):
        with checked_out(self.repository['testcontent'], semantic_change=True):
            pass
        lsc = zeit.cms.content.interfaces.ISemanticChange(self.repository['testcontent'])
        last_change = lsc.last_semantic_change
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent' '/@@workflow.html')
        b.getControl('Update last semantic change').selected = True
        b.getControl('Save state only').click()
        self.assertEllipsis('...Updated on...', b.contents)
        zope.component.hooks.setSite(self.getRootFolder())
        lsc = zeit.cms.content.interfaces.ISemanticChange(self.repository['testcontent'])
        self.assertGreater(lsc.last_semantic_change, last_change)

    # XXX we don't have a test content which is an asset available (#12013),
    # and using an ImageGroup is too much ZCML hassle
    # | def test_publish_asset(self):
    # |    b = self.browser
    # |    b.open('http://localhost/++skin++vivi/repository/testasset'
    # |           '/@@workflow.html')
    # |    b.getControl('Save state and publish now').click()
    # |    self.assertEllipsis('...Publication scheduled...', b.contents)


class ValidatingWorkflowFormTest(
    zeit.workflow.testing.FakeValidatingWorkflowMixin, zeit.workflow.testing.BrowserTestCase
):
    def test_publish_with_validation_error_displays_message(self):
        self.register_workflow_with_error()

        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent' '/@@workflow.html')
        b.getControl('Save state and publish now').click()
        self.assertEllipsis('...Validation Error Message...', b.contents)

    def test_publish_with_validation_warning_displays_message(self):
        self.register_workflow_with_warning()

        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent' '/@@workflow.html')
        b.getControl('Save state and publish now').click()
        self.assertEllipsis('...Validation Warning Message...', b.contents)
        zeit.workflow.testing.run_tasks()
