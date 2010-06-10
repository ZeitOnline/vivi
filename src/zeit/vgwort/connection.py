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
            # XXX figure out cache handling
            cache=suds.cache.NoCache())

    @property
    def wsdl(self):
        return urlparse.urljoin(self.config['vgwort-url'], self.service_path)

    @property
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration('zeit.vgwort')

    def __getattr__(self, name):
        try:
            getattr(self.client.service, name)
        except suds.MethodNotFound, e:
            raise AttributeError(str(e))
        return lambda *args, **kw: self.call(name, *args, **kw)

    def call(self, method_name, *args, **kw):
        try:
            method = getattr(self.client.service, method_name)
            return method(*args, **kw)
        except suds.WebFault, e:
            # the actual message is stored in a special response,
            # luckily the VGWort services employ a naming convention,
            # method 'foo' sends a fault as 'fooFault'.
            fault = getattr(e.fault.detail, method_name + 'Fault')
            # XXX unicode in Exceptions doesn't work
            message = fault.errormsg.encode('utf-8')
            raise zeit.vgwort.interfaces.WebServiceError(message)


class PixelService(VGWortWebService):

    zope.interface.implements(zeit.vgwort.interfaces.IPixelService)

    service_path = '/services/1.0/pixelService.wsdl'

    def order_pixels(self, amount):
        result = self.orderPixel(amount)
        for pixel in result.pixels.pixel:
            yield (pixel._publicIdentificationId,
                   pixel._privateIdentificationId)


class MessageService(VGWortWebService):

    zope.interface.implements(zeit.vgwort.interfaces.IMessageService)

    service_path = '/services/1.1/messageService.wsdl'

    def new_document(self, content):
        pass # nyi
