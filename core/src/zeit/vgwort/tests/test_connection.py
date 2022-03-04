from unittest import mock
import gocept.httpserverlayer.custom
import pkg_resources
import six
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

    def add_token(self, content):
        ts = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        ts.order(1)
        token = zeit.vgwort.interfaces.IToken(content)
        token.public_token, token.private_token = ts.claim()

    def test_smoketest_successful_call_roundtrip(self):
        result = self.service.call('qualityControl')
        self.assertGreater(len(result.qualityControlValues), 0)

    def test_validation_error_should_raise_error_message(self):
        products = list(zeit.cms.content.sources.PRODUCT_SOURCE(None))
        product = [x for x in products if x.id == 'KINZ'][0]
        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.product = product
        with self.assertRaises(zeit.vgwort.interfaces.WebServiceError) as e:
            self.service.new_document(self.repository['testcontent'])
        self.assertIn('privateidentificationid', str(e.exception))

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
            co.authorships = [co.authorships.create(shakespeare)]
            co.title = 'Title'
            co.teaserText = 'Das ist ein Blindtext.'
        content = self.repository['testcontent']
        self.add_token(content)

        try:
            self.service.new_document(content)
        except zeit.vgwort.interfaces.WebServiceError as e:
            self.assertIn('Shakespeare', six.text_type(e))
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
            co.authorships = [co.authorships.create(author)]
            co.title = 'Title'
            co.teaserText = 'Das ist ein Blindtext. ' * 2000
        content = self.repository['testcontent']
        self.add_token(content)

        try:
            self.service.new_document(content)
        except zeit.vgwort.interfaces.TechnicalError:
            self.skipTest('vgwort test system down')

    def test_author_without_vgwortid_works(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'Tina'
        author.lastname = 'Groll'
        self.repository['author'] = author
        author = self.repository['author']

        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.authorships = [co.authorships.create(author)]
            co.title = 'Title'
            co.teaserText = 'Das ist ein Blindtext. ' * 2000
        content = self.repository['testcontent']
        self.add_token(content)

        try:
            self.service.new_document(content)
        except zeit.vgwort.interfaces.TechnicalError:
            self.skipTest('vgwort test system down')

    def test_non_author_doc_as_author_should_be_ignored(self):
        import transaction
        import zeit.connector.interfaces
        author = zeit.content.author.author.Author()
        author.firstname = 'Tina'
        author.lastname = 'Groll'
        self.repository['tina'] = author
        author = self.repository['tina']

        author2 = zeit.content.author.author.Author()
        author2.firstname = 'Invalid'
        author2.lastname = 'stuff'
        self.repository['author2'] = author2
        author2 = self.repository['author2']
        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.authorships = [co.authorships.create(author),
                              co.authorships.create(author2)]
            co.title = 'Title'
            co.teaserText = 'Das ist ein Blindtext. ' * 2000
        content = self.repository['testcontent']
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        transaction.commit()
        connector._properties[u'http://xml.zeit.de/author2'][
            ('type', 'http://namespaces.zeit.de/CMS/meta')] = 'foo'
        self.add_token(content)

        try:
            self.service.new_document(content)
        except zeit.vgwort.interfaces.TechnicalError:
            self.skipTest('vgwort test system down')


class RequestHandler(gocept.httpserverlayer.custom.RequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        wsdl = pkg_resources.resource_string(__name__, 'pixelService.wsdl')
        wsdl = wsdl.decode().replace('__PORT__', str(HTTP_LAYER['http_port']))
        self.wfile.write(wsdl.encode())

    def do_POST(self):
        self.send_response(500)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', 0)
        self.end_headers()
        # suds expects SOAP or nothing (and may the Lord have mercy if the
        # server should return 500 with an HTML error message instead...)
        self.wfile.write('')


HTTP_LAYER = gocept.httpserverlayer.custom.Layer(
    RequestHandler, name='HTTPLayer', module=__name__)


class HTTPErrorTest(unittest.TestCase):

    layer = HTTP_LAYER

    def test_http_error_should_raise_technical_error(self):
        service = zeit.vgwort.connection.PixelService(
            'http://%s' % self.layer['http_address'], '', '')
        time.sleep(1)
        self.assertRaises(
            zeit.vgwort.interfaces.TechnicalError,
            lambda: list(service.order_pixels(1)))

    def test_connection_error_should_raise_technical_error(self):
        service = zeit.vgwort.connection.PixelService(
            'http://unavailable_address', '', '')
        time.sleep(1)
        with self.assertRaises(zeit.vgwort.interfaces.TechnicalError) as e:
            list(service.order_pixels(1))
        self.assertIn('ConnectionError', e.exception.args[0])


class MessageServiceTest(zeit.vgwort.testing.EndToEndTestCase):

    def setUp(self):
        super(MessageServiceTest, self).setUp()
        # Need a real webservice to load the WSDL.
        self.service = zope.component.getUtility(
            zeit.vgwort.interfaces.IMessageService)

    @property
    def repository(self):
        import zeit.cms.repository.interfaces
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def get_content(self, authors, freetext=None, product='KINZ'):
        products = list(zeit.cms.content.sources.PRODUCT_SOURCE(None))
        product = [x for x in products if x.id == product]
        content = self.repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.authorships = [co.authorships.create(x) for x in authors]
            co.authors = freetext
            if product:
                co.product = product[0]
            co.title = 'Title'
            co.teaserText = 'x' * 2000
        return self.repository['testcontent']

    def test_content_must_have_commonmetadata(self):
        with self.assertRaises(zeit.vgwort.interfaces.WebServiceError) as e:
            self.service.new_document(mock.sentinel.notanarticle)
        self.assertEqual(
            e.exception.args,
            ('Artikel existiert nicht mehr.',))

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
        self.assertEqual('1234abc', authors[-1].code__1)

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
        self.assertEqual('codecodecode', authors[0].code__1)

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

    def test_only_authors_with_configured_roles_should_be_reported(self):
        tina = zeit.content.author.author.Author()
        tina.firstname = 'Tina'
        tina.vgwortcode = 'Groll'
        self.repository['tina'] = tina
        paul = zeit.content.author.author.Author()
        paul.firstname = 'Paul'
        paul.vgwortcode = 'Auster'
        paul.vgwortcode = 'code'
        self.repository['paul'] = paul
        content = self.get_content([], product=None)
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.authorships = [co.authorships.create(tina),
                              co.authorships.create(paul)]
            co.authorships[0].role = u'Illustration'
            co.authorships[1].role = u'Visualisierung'
        content = self.repository['testcontent']
        with mock.patch('zeit.vgwort.connection.MessageService.call') as call:
            self.service.new_document(content)
            parties = call.call_args[0][1]
            authors = parties.authors.author
        self.assertEqual(1, len(authors))
        self.assertEqual('code', authors[0].code__1)

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

    def test_freetext_authors_should_be_whitespace_normalized(self):
        content = self.get_content(
            [], freetext=(
                ('  Paul   Auster  ', '  Hans   Christian   Andersen  ')))
        with mock.patch('zeit.vgwort.connection.MessageService.call') as call:
            self.service.new_document(content)
            parties = call.call_args[0][1]
            authors = parties.authors.author
        self.assertEqual(3, len(authors))  # two author, one product
        self.assertEqual('Paul', authors[0].firstName)
        self.assertEqual('Auster', authors[0].surName)
        self.assertEqual('Hans Christian', authors[1].firstName)
        self.assertEqual('Andersen', authors[1].surName)
