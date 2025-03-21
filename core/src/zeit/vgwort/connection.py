import logging
import random
import threading
import urllib.parse

from zope.cachedescriptors.property import Lazy as cachedproperty
import requests
import requests.auth
import requests.exceptions
import zeep
import zeep.exceptions
import zope.interface

import zeit.cms.config
import zeit.content.author.interfaces
import zeit.vgwort.interfaces


log = logging.getLogger(__name__)


class VGWortWebService:
    """This class handles the configuration of URL and authentication
    information, and provides better error handling for errors returned by the
    web service.

    Subclasses should override `service_path` to point to the WSDL file, and
    can then call the service's methods on themselves, e. g. if the web service
    provides a method 'orderPixel', call it as self.orderPixel(args).
    """

    # override in subclass
    service_path = None
    namespace = None

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.lock = threading.Lock()
        session = requests.Session()
        session.auth = requests.auth.HTTPBasicAuth(username, password)
        self.transport = zeep.Transport(session=session)

    @cachedproperty
    def client(self):
        # We intenionally don't cache the WSDL file, since that leads to
        # intransparent behaviour when debugging.
        # This means it is downloaded afresh every time, but that doesn't
        # occur often, as the utility is instantiated only once, so it's
        # not performance critical other otherwise bad.
        try:
            client = zeep.Client(self.wsdl, transport=self.transport)
        finally:
            self.transport.session.close()
        return client

    @property
    def wsdl(self):
        return urllib.parse.urljoin(self.base_url, self.service_path)

    def call(self, method_name, *args, **kw):
        with self.lock:
            try:
                method = getattr(self.client.service, method_name)
                result = method(*args, **kw)
                if isinstance(result, tuple):
                    raise zeit.vgwort.interfaces.TechnicalError(result)
                return result
            except zeep.exceptions.Fault as e:
                if e.detail is not None:
                    node = e.detail.getchildren()[0]
                    message = node.find('{%s}errormsg' % self.namespace)
                    code = node.find('{%s}errorcode' % self.namespace)
                    code = int(code.text) if code is not None else 0
                else:
                    message = None
                    code = 999
                message = message.text if message is not None else 'unknown'
                if code >= 100:
                    raise zeit.vgwort.interfaces.TechnicalError(message)
                raise zeit.vgwort.interfaces.WebServiceError(message)
            except zeep.exceptions.ValidationError as e:
                raise zeit.vgwort.interfaces.WebServiceError(e.message)
            except zeep.exceptions.TransportError as e:
                raise zeit.vgwort.interfaces.TechnicalError(e.message)
            except requests.exceptions.RequestException as e:
                # No e.message available here.
                raise zeit.vgwort.interfaces.TechnicalError(str(e))
            finally:
                try:
                    self.transport.session.close()
                except Exception:
                    pass

    def create(self, type_, **kw):
        cls = self.client.get_type('{%s}%s' % (self.namespace, type_))
        return cls(**kw)


@zope.interface.implementer(zeit.vgwort.interfaces.IPixelService)
class PixelService(VGWortWebService):
    service_path = '/services/1.0/pixelService.wsdl'
    namespace = 'http://vgwort.de/1.0/PixelService/xsd'

    def order_pixels(self, amount):
        log.info('orderPixel, amount=%s', amount)
        result = self.call('orderPixel', amount)
        for pixel in result.pixels.pixel:
            yield (pixel.publicIdentificationId, pixel.privateIdentificationId)


@zope.interface.implementer(zeit.vgwort.interfaces.IMessageService)
class MessageService(VGWortWebService):
    service_path = '/services/2.0/messageService.wsdl'
    namespace = 'http://vgwort.de/2.0/MessageService/xsd'

    def new_document(self, content):
        content = zeit.cms.content.interfaces.ICommonMetadata(content, None)
        if content is None:
            raise zeit.vgwort.interfaces.WebServiceError('Artikel existiert nicht mehr.')
        authors = []
        if content.authorships:
            ROLES = zeit.content.author.interfaces.ROLE_SOURCE(None)
            for author in content.authorships:
                if not ROLES.report_to_vgwort(author.role):
                    continue
                author = author.target
                if author is None:
                    continue
                try:
                    if author.vgwort_code:
                        # XXX Is this case still needed? Is there still content
                        # that references agencies in ICommonMetadata.authorships
                        # instead of .agencies? And are we *ever* going to report
                        # such content (again)?
                        authors.append(self.create('Involved', code=author.vgwort_code))
                    elif (
                        author.firstname
                        and author.lastname
                        and author.firstname.strip()
                        and author.lastname.strip()
                    ):
                        params = {'firstName': author.firstname, 'surName': author.lastname}
                        if author.vgwort_id:
                            params['cardNumber'] = author.vgwort_id
                        authors.append(self.create('Involved', **params))
                except AttributeError:
                    log.error('Could not report %s', content, exc_info=True)

        for author in content.agencies:
            try:
                if not author.vgwort_code:
                    continue
                authors.append(self.create('Involved', code=author.vgwort_code))
            except AttributeError:
                log.warning('Ignoring agencies for %s', content, exc_info=True)
        if content.product and content.product.vgwort_code:
            authors.append(self.create('Involved', code=content.product.vgwort_code))

        if not authors:
            raise zeit.vgwort.interfaces.WebServiceError('Kein Autor mit VG-Wort-Code gefunden.')

        searchable = zope.index.text.interfaces.ISearchableText(content)
        text = self.create(
            'MessageText',
            lyric=False,
            shorttext=content.title[:100],
            text=self.create(
                'Text', plainText='\n'.join(searchable.getSearchableText()).encode('utf-8')
            ),
        )

        public_url = (
            content.uniqueId.replace('http://xml.zeit.de', 'http://www.zeit.de')
            + '/komplettansicht'
        )
        ranges = self.create('Webranges', webrange=[self.create('Webrange', url=public_url)])

        token = zeit.vgwort.interfaces.IToken(content)
        parties = self.create('Parties', authors=self.create('Authors', author=authors))
        self.call(
            'newMessage',
            parties,
            text,
            ranges,
            privateidentificationid=token.private_token,
            reproductionRight=True,
            distributionRight=True,
            publicAccessRight=True,
            otherRightsOfPublicReproduction=True,
            rightsGrantedConfirmation=True,
            withoutOwnParticipation=False,
        )


def service_factory(TYPE):
    def factory():
        config = zeit.cms.config.package('zeit.vgwort')
        return TYPE(config['vgwort-url'], config['username'], config['password'])

    factory = zope.interface.implementer(list(zope.interface.implementedBy(TYPE))[0])(factory)
    return factory


real_pixel_service = service_factory(PixelService)
real_message_service = service_factory(MessageService)


@zope.interface.implementer(zeit.vgwort.interfaces.IPixelService)
class MockPixelService:
    def order_pixels(self, amount):
        offset = 100_000 + random.randint(1, 100) * 1000
        for i in range(amount):
            n = offset + i
            yield ('public-%s' % n, 'private-%s' % n)


@zope.interface.implementer(zeit.vgwort.interfaces.IMessageService)
class MockMessageService:
    def __init__(self):
        self.reset()

    def reset(self):
        self.calls = []
        self.error = None

    def new_document(self, content):
        if self.error:
            raise self.error('Provoked error')
        self.calls.append(content)
