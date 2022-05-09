from unittest import mock
from zeit.newsletter.newsletter import Newsletter
import transaction
import zeit.cms.testing
import zeit.newsletter.testing


class WorkflowTest(zeit.newsletter.testing.BrowserTestCase):

    def setUp(self):
        super().setUp()
        self.repository['newsletter'] = Newsletter()
        zeit.cms.workflow.interfaces.IPublishInfo(
            self.repository['newsletter']).published = False
        transaction.commit()

    def test_send_button_should_perform_both_normal_publish_and_send(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/newsletter/@@workflow.html')
        self.assertFalse(b.getControl('Published').selected)
        with mock.patch('zeit.newsletter.newsletter.Newsletter.send') as send:
            b.getControl('Send emails and publish now').click()
            self.assertTrue(send.called)
        b.reload()
        self.assertTrue(b.getControl('Published').selected)
        self.assertTrue(b.getControl('Sent').selected)

    def test_email_address_is_populated_from_principal(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/newsletter/@@workflow.html')
        self.assertIn('test@example.com', b.getControl('Email for test').value)

    def test_email_address_can_be_overridden_in_session(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/newsletter/@@workflow.html')
        b.getControl('Email for test').value = 'other@example.com'
        b.getControl('Save state only').click()
        b.reload()
        self.assertEqual(
            'other@example.com', b.getControl('Email for test').value)

    def test_email_address_is_passed_to_send_test(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/newsletter/@@workflow.html')
        b.getControl('Email for test').value = 'other@example.com'
        with mock.patch(
                'zeit.newsletter.newsletter.Newsletter.send_test') as send:
            send.__Security_checker__ = mock.Mock()
            b.getControl('Test email').click()
            send.assert_called_with('other@example.com')
