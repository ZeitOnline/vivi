# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import pkg_resources
import time
import unittest
import zeit.cms.checkout.helper
import zeit.vgwort.connection
import zeit.vgwort.interfaces
import zeit.vgwort.testing
import zope.component


class WebServiceTest(zeit.vgwort.testing.EndToEndTestCase):

    def setUp(self):
        super(WebServiceTest, self).setUp()
        self.service = zope.component.getUtility(
            zeit.vgwort.interfaces.IMessageService)

    @property
    def repository(self):
        import zeit.cms.repository.interfaces
        return zope.component.getUtility(
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
        products = list(zeit.cms.content.sources.ProductSource()(None))
        product = [x for x in products if x.id == 'KINZ'][0]
        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.product = product
        try:
            self.service.new_document(self.repository['testcontent'])
        except TypeError, e:
            self.assertContains(
                "The value 'None' of attribute 'privateidentificationid'",
                str(e))
        else:
            self.fail('TypeError should have been raised.')

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
            self.assertContains('Shakespeare', unicode(e))
        else:
            self.fail('WebServiceError should have been raised.')

    def test_report_new_document(self):
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

    def test_author_without_vgwotid_works(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'Tina'
        author.lastname = 'Groll'
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


class RequestHandler(zeit.cms.testing.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        wsdl = pkg_resources.resource_string(__name__, 'pixelService.wsdl')
        wsdl = wsdl.replace('__PORT__', str(port))
        self.wfile.write(wsdl)

    def do_POST(self):
        self.send_response(500)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', 0)
        self.end_headers()
        # suds expects SOAP or nothing (and may the Lord have mercy if the
        # server should return 500 with an HTML error message instead...)
        self.wfile.write('')


HTTPLayer, port = zeit.cms.testing.HTTPServerLayer(RequestHandler)


class HTTPErrorTest(unittest.TestCase):

    layer = HTTPLayer

    def test_http_error_should_raise_technical_error(self):
        service = zeit.vgwort.connection.PixelService(
            'http://localhost:%s' % port, '', '')
        time.sleep(1)
        self.assertRaises(
            zeit.vgwort.interfaces.TechnicalError,
            lambda: list(service.order_pixels(1)))


class MessageServiceTest(zeit.vgwort.testing.TestCase):

    def setUp(self):
        super(MessageServiceTest, self).setUp()
        # Need a real webservice to load the WSDL.
        self.service = zeit.vgwort.connection.real_message_service()

    @property
    def repository(self):
        import zeit.cms.repository.interfaces
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def get_content(self, authors, freetext=None):
        products = list(zeit.cms.content.sources.ProductSource()(None))
        product = [x for x in products if x.id == 'KINZ'][0]
        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.author_references = authors
            co.authors = freetext
            co.product = product
            co.title = 'Title'
            co.teaserText = 'x' * 2000
        return self.repository['testcontent']

    def test_content_must_have_commonmetadata(self):
        self.assertRaises(
            TypeError, self.service.new_document, None)

    def test_product_is_passed_as_additional_author_with_code(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'Tina'
        author.lastname = 'Groll'
        author.vgwortid = 2601970
        self.repository['author'] = author
        author = self.repository['author']
        content = self.get_content([author])
        with mock.patch('zeit.vgwort.connection.MessageService.call') as call:
            self.service.new_document(content)
            parties = call.call_args[0][1]
            authors = parties.authors.author
        self.assertEqual(2, len(authors))
        self.assertEqual('1234abc', authors[-1].code)

    def test_author_code_should_be_passed_instead_of_name(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'Tina'
        author.lastname = 'Groll'
        author.vgwortid = 2601970
        author.vgwortcode = 'codecodecode'
        self.repository['author'] = author
        author = self.repository['author']
        content = self.get_content([author])
        with mock.patch('zeit.vgwort.connection.MessageService.call') as call:
            self.service.new_document(content)
            parties = call.call_args[0][1]
            authors = parties.authors.author
        self.assertEqual(2, len(authors))
        self.assertEqual('codecodecode', authors[0].code)

    def test_author_name_should_be_passed(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'Tina'
        author.lastname = 'Groll'
        self.repository['author'] = author
        author = self.repository['author']
        content = self.get_content([author])
        with mock.patch('zeit.vgwort.connection.MessageService.call') as call:
            self.service.new_document(content)
            parties = call.call_args[0][1]
            authors = parties.authors.author
        self.assertEqual(2, len(authors))
        self.assertEqual('Tina', authors[0].firstName)
        self.assertEqual('Groll', authors[0].surName)

    def test_url_should_point_to_www_zeit_de(self):
        content = self.get_content([])
        with mock.patch('zeit.vgwort.connection.MessageService.call') as call:
            self.service.new_document(content)
            self.assertEqual('http://www.zeit.de/testcontent/komplettansicht',
                             call.call_args[0][3].webrange[0].url)

    def test_freetext_authors_should_be_passed(self):
        content = self.get_content(
            [], freetext=(('Paul Auster', 'Hans Christian Andersen')))
        with mock.patch('zeit.vgwort.connection.MessageService.call') as call:
            self.service.new_document(content)
            parties = call.call_args[0][1]
            authors = parties.authors.author
        self.assertEqual(3, len(authors))  # two author, one product
        self.assertEqual('Paul', authors[0].firstName)
        self.assertEqual('Auster', authors[0].surName)
        self.assertEqual('Hans Christian', authors[1].firstName)
        self.assertEqual('Andersen', authors[1].surName)

    def test_freetext_authors_should_be_passed_unless_structured_given(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'Tina'
        author.lastname = 'Groll'
        self.repository['author'] = author
        author = self.repository['author']
        content = self.get_content(
            [author], freetext=(('Paul Auster', 'Hans Christian Andersen')))
        with mock.patch('zeit.vgwort.connection.MessageService.call') as call:
            self.service.new_document(content)
            parties = call.call_args[0][1]
            authors = parties.authors.author
        self.assertEqual(2, len(authors))
        self.assertEqual('Tina', authors[0].firstName)
        self.assertEqual('Groll', authors[0].surName)

    def test_freetext_authors_should_not_break_with_no_space(self):
        content = self.get_content(
            [], freetext=(('Merlin',)))
        with mock.patch('zeit.vgwort.connection.MessageService.call') as call:
            self.service.new_document(content)
            parties = call.call_args[0][1]
            authors = parties.authors.author
        self.assertEqual(1, len(authors))  # one product
