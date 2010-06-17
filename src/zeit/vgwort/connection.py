# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import suds
import suds.cache
import suds.client
import urlparse
import zeit.vgwort.interfaces
import zope.app.appsetup.product
import zope.interface


class VGWortWebService(object):
    """This class handles the configuration of URL and authentication
    information, and provides better error handling for errors returned by the
    web service.

    Subclasses should override `service_path` to point to the WSDL file, and
    can then call the service's methods on themselves, e. g. if the web service
    provides a method 'orderPixel', call it as self.orderPixel(args).
    """

    service_path = None # override in subclass

    def __init__(self):
        self.client = suds.client.Client(
            self.wsdl,
            username=self.config['username'],
            password=self.config['password'],
            # disable caching of the WSDL file, since it leads to intransparent
            # behaviour when debugging.
            # This means it is downloaded afresh every time, but that doesn't
            # occur often, as the utility is instantiated only once (on server
            # startup), so it's not performance critical other otherwise bad.
            cache=suds.cache.NoCache())

    @property
    def wsdl(self):
        return urlparse.urljoin(self.config['vgwort-url'], self.service_path)

    @property
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration('zeit.vgwort')

    def call(self, method_name, *args, **kw):
        try:
            method = getattr(self.client.service, method_name)
            return method(*args, **kw)
        except suds.WebFault, e:
            raise zeit.vgwort.interfaces.WebServiceError(
                str(e.fault.detail[0]))

    def create(self, type_):
        return self.client.factory.create('ns0:%s' % type_)


class PixelService(VGWortWebService):

    zope.interface.implements(zeit.vgwort.interfaces.IPixelService)

    service_path = '/services/1.0/pixelService.wsdl'

    def order_pixels(self, amount):
        result = self.call('orderPixel', amount)
        for pixel in result.pixels.pixel:
            yield (pixel._publicIdentificationId,
                   pixel._privateIdentificationId)


class MessageService(VGWortWebService):

    zope.interface.implements(zeit.vgwort.interfaces.IMessageService)

    service_path = '/services/1.1/messageService.wsdl'

    def new_document(self, content):
        content = zeit.cms.content.interfaces.ICommonMetadata(content)
        parties = self.create('Parties')
        parties.authors = self.create('Authors')
        for author in content.author_references:
            involved = self.create('Involved')
            involved.firstName = author.firstname
            involved.surName = author.lastname
            involved.cardNumber = author.vgwortid
            parties.authors.author.append(involved)

        text = self.create('MessageText')
        text.text = self.create('Text')
        text._lyric = False
        text.shorttext = content.title
        searchable = zope.index.text.interfaces.ISearchableText(content)
        text.text.plainText = u'\n'.join(
            searchable.getSearchableText()).encode('utf-8').encode('base64')

        ranges = self.create('Webranges')
        url = self.create('Webrange')
        url.url = content.uniqueId.replace(
            'http://xml.zeit.de', 'http://www.zeit.de')
        ranges.webrange.append(url)

        token = zeit.vgwort.interfaces.IToken(content)
        self.call('newMessage', parties, text, ranges,
                  privateidentificationid=token.private_token)
