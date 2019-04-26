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
            message = str(e)
            if message == 'None':
                # BeautifulSoup using HTMLParser used to be able to say
                # "malformed start tag" in some cases, but that behaviour has
                # been removed in Python-2.7.4
                message = 'Not valid XML'
            raise zope.schema.ValidationError(message)

    def set(self, object, value):
        if self.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.__name__,
                               object.__class__.__module__,
                               object.__class__.__name__))
        current_value = self.query(object, DEFAULT_MARKER)
        if not (current_value is DEFAULT_MARKER or
                current_value.getparent() is None):
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


class XMLSnippet(zope.schema.Text):

    zope.interface.implements(IXMLSnippet)

    def __init__(self, subset=None, **kwargs):
        if subset is None:
            subset = zeit.cms.content.cmssubset.CMS_SUBSET
        self.subset = subset
        super(XMLSnippet, self).__init__(**kwargs)

    def fromUnicode(self, value):
        if not isinstance(value, unicode):
            raise TypeError("Expected unicode, got %s" % type(value))
        value = self._filter(value)
        return super(XMLSnippet, self).fromUnicode(value)

    def _validate(self, value):
        super(XMLSnippet, self)._validate(value)
        if value != self._filter(value):
            raise InvalidXML()

    def _filter(self, value):
        if self.subset is not None:
            # We need a dom where we can append the values.
            dom = xml.dom.minidom.parseString('<xml/>')
            value = self.subset.filteredParse(value, dom.firstChild)
            value = u''.join(node.toxml() for node in value.childNodes)
        return value


class Color(zope.schema.TextLine):
    pass
