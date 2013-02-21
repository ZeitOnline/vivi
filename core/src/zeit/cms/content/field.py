# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.content.util import objectify_soup_fromstring
from zeit.cms.i18n import MessageFactory as _
import HTMLParser
import lxml.etree
import lxml.objectify
import xml.dom.minidom
import zeit.cms.content.cmssubset
import zope.interface
import zope.location.location
import zope.proxy
import zope.schema
import zope.schema.interfaces
import zope.security._proxy
import zope.security.checker
import zope.security.proxy


DEFAULT_MARKER = object()


class IXMLTree(zope.schema.interfaces.IField):
    """A field containing an lxml.objectified tree."""
    # This is here to avoid circular imports


class IXMLSnippet(zope.schema.interfaces.IField):
    """A field containing an xml-snippet."""


class InvalidXML(zope.schema.interfaces.ValidationError):
    __doc__ = _('Invalid structure.')


class _XMLBase(zope.schema.Field):

    zope.interface.implements(zope.schema.interfaces.IFromUnicode)

    def __init__(self, *args, **kw):
        tidy_input = kw.pop('tidy_input', False)
        if tidy_input:
            self.parse = objectify_soup_fromstring
        else:
            self.parse = lxml.objectify.fromstring
        super(_XMLBase, self).__init__(*args, **kw)

    def fromUnicode(self, text):
        try:
            return self.parse(text)
        except (lxml.etree.XMLSyntaxError, ValueError,
                HTMLParser.HTMLParseError), e:
            raise zope.schema.ValidationError(str(e))

    def set(self, object, value):
        if self.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.__name__,
                               object.__class__.__module__,
                               object.__class__.__name__))
        current_value = self.query(object, DEFAULT_MARKER)
        if not (current_value is DEFAULT_MARKER
                or current_value.getparent() is None):
            # Locate the XML object into the workingcopy so that edit
            # permissions can be found
            parent = located(current_value.getparent(), object, self.__name__)
            # Remove the security proxy cause lxml can't eat them
            parent.replace(
                zope.security.proxy.removeSecurityProxy(current_value), value)
        setattr(object, self.__name__, value)


def located(obj, parent, name):
    obj_ = zope.security.proxy.removeSecurityProxy(obj)
    obj_ = zope.location.location.LocationProxy(
        obj_, parent, name)
    if type(obj) == zope.security._proxy._Proxy:
        return zope.security.checker.ProxyFactory(obj_)
    return obj_


class XMLTree(_XMLBase):

    zope.interface.implements(IXMLTree)
