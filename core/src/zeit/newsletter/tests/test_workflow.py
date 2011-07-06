# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.newsletter.newsletter import Newsletter
import mock
import zeit.newsletter.testing


class SendEmailTest(zeit.newsletter.testing.TestCase):

    def test_should_call_send_and_mark_as_sent(self):
        ANY = None
        newsletter = Newsletter()
        info = zeit.cms.workflow.interfaces.IPublishInfo(newsletter)
        self.assertFalse(info.sent)
        with mock.patch.object(newsletter, 'send') as send:
            zeit.newsletter.workflow.send_email(newsletter, ANY)
            self.assertTrue(send.called)
        self.assertTrue(info.sent)

    def test_already_sent_should_not_call_send_again(self):
        ANY = None
        newsletter = Newsletter()
        info = zeit.cms.workflow.interfaces.IPublishInfo(newsletter)
        info.sent = True
        with mock.patch.object(newsletter, 'send') as send:
            zeit.newsletter.workflow.send_email(newsletter, ANY)
            self.assertFalse(send.called)
