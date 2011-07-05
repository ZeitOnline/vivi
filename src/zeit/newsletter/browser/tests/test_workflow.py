# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.newsletter.newsletter import Newsletter
import lovely.remotetask
import transaction
import zeit.cms.testing
import zeit.newsletter.testing
import zope.component


class WorkflowTest(zeit.newsletter.testing.BrowserTestCase):

    def setUp(self):
        super(WorkflowTest, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.repository['newsletter'] = Newsletter()
            zeit.cms.workflow.interfaces.IPublishInfo(
                self.repository['newsletter']).published = False
        transaction.commit()

    def run_tasks(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            tasks = zope.component.getUtility(
                lovely.remotetask.interfaces.ITaskService, 'general')
            zeit.cms.testing.create_interaction()
            transaction.abort()
            tasks.process()
            zope.security.management.endInteraction()

    def test_send_button_should_perform_normal_publish(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/newsletter/@@workflow.html')
        self.assertFalse(b.getControl('Published').selected)
        b.getControl('Send emails and publish now').click()
        self.run_tasks()
        b.reload()
        self.assertTrue(b.getControl('Published').selected)

    def test_send_button_should_send_email_via_optivo(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/newsletter/@@workflow.html')
        self.assertFalse(b.getControl('Published').selected)
        b.getControl('Send emails and publish now').click()
        self.run_tasks()
        b.reload()
        self.assertTrue(b.getControl('Sent').selected, 'nyi')
