# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import logging
import lxml.etree
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.connector.resource
import zope.interface


log = logging.getLogger(__name__)
# Marker object to indicate no add form.
SKIP_ADD = object()


class TypeDeclaration(object):

    interface = None
    interface_type = zeit.cms.interfaces.ICMSContentType

    # The "type" in DAV. If given the class will also implement IDAVContent
    type = None
    title = None
    addform = None
    register_as_type = True

    def __init__(self):
        if self.addform is None:
            package = '.'.join(self.__module__.split('.')[:-1])
            self.addform = package + '.Add'

    def content(self, resource):
        raise NotImplementedError

    def resource_body(self, content):
        raise NotImplementedError

    def resource_content_type(self, content):
        return None

    def resource_properties(self, content):
        try:
            return zeit.connector.interfaces.IWebDAVReadProperties(content)
        except TypeError:
            return zeit.connector.resource.WebDAVProperties()

    def resource(self, content):
        return zeit.connector.resource.Resource(
            content.uniqueId, content.__name__, self.type,
            data=self.resource_body(content),
            contentType=self.resource_content_type(content),
            properties=self.resource_properties(content))

    @property
    def type_identifier(self):
        if self.type is not None:
            return self.type
        assert self.interface is not None
        return u'%s.%s' % (self.interface.__module__, self.interface.__name__)


class XMLContentTypeDeclaration(TypeDeclaration):

    factory = None

    def content(self, resource):
        try:
            return self.factory(xml_source=resource.data)
        except lxml.etree.XMLSyntaxError, e:
            log.warning("Could not parse XML of %s: %s (%s)" % (
                resource.id, e.__class__.__name__, e))
            return None

    def resource_body(self, content):
        return StringIO.StringIO(
            zeit.cms.content.interfaces.IXMLSource(content))

    def resource_content_type(self, content):
        return 'text/xml'


def get_type(self, content):
    for interface in zope.interface.providedBy(content):
        try:
            return interface.getTaggedValue('zeit.cms.type')
        except KeyError:
            continue
    return None
