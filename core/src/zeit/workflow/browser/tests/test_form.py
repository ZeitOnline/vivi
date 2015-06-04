import zeit.cms.testing
import zeit.workflow.testing


class WorkflowFormTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.workflow.testing.LAYER

    def test_publish_content(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent'
               '/@@workflow.html')
        b.getControl('Urgent').click()
        b.getControl('Save state and publish now').click()
        self.assertEllipsis('...Publication scheduled...', b.contents)

    # XXX we don't have a test content which is an asset available (#12013),
    # and using an ImageGroup is too much ZCML hassle
    # def test_publish_asset(self):
    #     b = self.browser
    #     b.open('http://localhost/++skin++vivi/repository/testasset'
    #            '/@@workflow.html')
    #     b.getControl('Save state and publish now').click()
    #     self.assertEllipsis('...Publication scheduled...', b.contents)


class ValidatingWorkflowFormTest(
        zeit.workflow.testing.FakeValidatingWorkflowMixin,
        zeit.cms.testing.BrowserTestCase):

    layer = zeit.workflow.testing.LAYER

    def test_publish_with_validation_error_displays_message(self):
        self.register_workflow_with_error()

        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent'
               '/@@workflow.html')
        b.getControl('Save state and publish now').click()
        self.assertEllipsis('...publish-preconditions-not-met...', b.contents)
        self.assertEllipsis('...Validation Error Message...', b.contents)

    def test_publish_with_validation_warning_displays_message(self):
        self.register_workflow_with_warning()

        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent'
               '/@@workflow.html')
        b.getControl('Save state and publish now').click()
        self.assertEllipsis('...scheduled for publishing...', b.contents)
        self.assertEllipsis('...Validation Warning Message...', b.contents)
