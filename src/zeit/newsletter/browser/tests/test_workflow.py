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

    def test_send_button_should_perform_both_normal_publish_and_send(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/newsletter/@@workflow.html')
        self.assertFalse(b.getControl('Published').selected)
        b.getControl('Send emails and publish now').click()
        self.run_tasks()
        b.reload()
        self.assertTrue(b.getControl('Published').selected)
        self.assertTrue(b.getControl('Sent').selected)

    def test_email_address_is_populated_from_principal(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/newsletter/@@workflow.html')
        # XXX
        self.assertIn(
            'not yet implemented', b.getControl('Email for test').value)

    def test_email_address_can_be_overridden_in_session(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/newsletter/@@workflow.html')
        b.getControl('Email for test').value = 'other@example.com'
        b.getControl('Save state only').click()
        b.reload()
        self.assertEqual(
            'other@example.com', b.getControl('Email for test').value)
