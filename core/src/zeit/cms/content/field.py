# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.etree
import lxml.objectify

import zope.interface
import zope.proxy
import zope.schema
import zope.schema.interfaces

import zope.app.form.browser.textwidgets
import zope.app.form.interfaces


DEFAULT_MARKER = object()


class IXMLTree(zope.schema.interfaces.IField):
    """A field containing an lxml.objectified tree."""
    # This is here to avoid circular imports

class XMLTree(zope.schema.Field):

    zope.interface.implements(
        IXMLTree,
        zope.schema.interfaces.IFromUnicode)

    def fromUnicode(self, str):
        try:
            return lxml.objectify.fromstring(str)
        except (lxml.etree.XMLSyntaxError, ValueError), e:
                raise zope.schema.ValidationError(e)

    def set(self, object, value):
        if self.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.__name__,
                               object.__class__.__module__,
                               object.__class__.__name__))
        current_value = self.query(object, DEFAULT_MARKER)
        if (current_value is DEFAULT_MARKER
            or current_value.getparent() is None):
            setattr(object, self.__name__, value)
        else:
            current_value[:] = [value]


class XMLTreeWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def _toFieldValue(self, input):
        try:
            return self.context.fromUnicode(input)
        except zope.schema.ValidationError, e:
            raise zope.app.form.interfaces.ConversionError(e)

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        else:
            # Etree very explicitly checks for the type and doesn't like a
            # proxied object
            value = zope.proxy.removeAllProxies(value)
            return lxml.etree.tounicode(value, pretty_print=True).replace(
                '\n', '\r\n')
