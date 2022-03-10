from zeit.cms.content.util import objectify_soup_fromstring
import lxml.etree
import lxml.objectify
import zope.interface
import zope.location.location
import zope.proxy
import zope.schema
import zope.schema.interfaces
import zope.security.checker
import zope.security.proxy


DEFAULT_MARKER = object()


class IXMLTree(zope.schema.interfaces.IField):
    """A field containing an lxml.objectified tree."""
    # This is here to avoid circular imports


@zope.interface.implementer(zope.schema.interfaces.IFromUnicode)
class _XMLBase(zope.schema.Field):

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
        except (lxml.etree.XMLSyntaxError, ValueError) as e:
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
    if type(obj) == zope.security.proxy.Proxy:
        return zope.security.checker.ProxyFactory(obj_)
    return obj_


@zope.interface.implementer(IXMLTree)
class XMLTree(_XMLBase):
    pass


class Color(zope.schema.TextLine):
    pass


EMPTY = object()


def apply_default_values(context, interface, set_none=False):
    """Apply default values from ``interface`` to ``context``."""
    for name, field in zope.schema.getFields(interface).items():
        if field.readonly:
            continue
        __traceback_info__ = (name,)
        default = getattr(field, 'default')
        # don't set None values (#9406)
        if default is None and not set_none:
            continue
        current = getattr(context, name, EMPTY)
        # don't cause a field to be written unnecessarily
        if current == default:
            continue
        # if a value exists, don't overwrite it
        if current is not EMPTY and current is not field.missing_value:
            continue
        setattr(context, name, default)
