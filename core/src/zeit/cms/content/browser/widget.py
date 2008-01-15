# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.etree

import zope.app.form.browser.textwidgets
import zope.app.form.interfaces


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
            if value.getparent() is None:
                # When we're editing the whole tree we want to serialize the
                # root tree to get processing instructions.
                value = value.getroottree()
            return lxml.etree.tounicode(value, pretty_print=True).replace(
                '\n', '\r\n')
