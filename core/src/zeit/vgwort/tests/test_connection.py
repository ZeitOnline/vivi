# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.checkout.helper
import zeit.cms.repository.interfaces
import zeit.vgwort.connection
import zeit.vgwort.interfaces
import zeit.vgwort.testing
import zope.component


class WebServiceTest(zeit.vgwort.testing.EndToEndTestCase):

    def setUp(self):
        super(WebServiceTest, self).setUp()
        self.service = zope.component.getUtility(
            zeit.vgwort.interfaces.IMessageService)
        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def assertContains(self, needle, haystack):
        if needle not in haystack:
            self.fail(u"%r was not found in %r" % (needle, haystack))

    def add_token(self, content):
        ts = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        ts.order(1)
        token = zeit.vgwort.interfaces.IToken(content)
        token.public_token, token.private_token = ts.claim()

    def test_smoketest_successful_call_roundtrip(self):
        result = self.service.call('qualityControl')
        self.assert_(len(result.qualityControlValues) > 0)

    def test_validation_error_should_raise_error_message(self):
        try:
            self.service.new_document(self.repository['testcontent'])
        except zeit.vgwort.interfaces.WebServiceError, e:
            self.assertContains(
                "The value 'None' of attribute 'privateidentificationid'",
                str(e))
        else:
            self.fail('WebServiceError should have been raised.')

    def test_business_fault_should_raise_error_message(self):
        shakespeare = zeit.content.author.author.Author()
        shakespeare.title = 'Sir'
        shakespeare.firstname = 'William'
        shakespeare.lastname = 'Shakespeare'
        shakespeare.vgwortid = 12345
        self.repository['shakespeare'] = shakespeare
        shakespeare = self.repository['shakespeare']

        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.author_references = [shakespeare]
            co.title = 'Title'
            co.teaserText = 'asdf'
        content = self.repository['testcontent']
        self.add_token(content)

        try:
            self.service.new_document(content)
        except zeit.vgwort.interfaces.WebServiceError, e:
            self.assertContains('Shakespeare', str(e))
        else:
            self.fail('WebServiceError should have been raised.')

    def test_register_new_document(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'Tina'
        author.lastname = 'Groll'
        author.vgwortid = 2601970
        self.repository['author'] = author
        author = self.repository['author']

        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.author_references = [author]
            co.title = 'Title'
            co.teaserText = 'x' * 2000
        content = self.repository['testcontent']
        self.add_token(content)

        self.service.new_document(content)


class MessageServiceTest(zeit.vgwort.testing.TestCase):

    def setUp(self):
        super(MessageServiceTest, self).setUp()
        self.service = zeit.vgwort.connection.MessageService()
        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def test_content_must_have_commonmetadata(self):
        self.assertRaises(
            TypeError, self.service.new_document, None)
