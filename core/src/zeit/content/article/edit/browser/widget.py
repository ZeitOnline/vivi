# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from xml.sax.saxutils import escape
import re
import zope.formlib.source


class BadgeInputWidget(zope.formlib.source.SourceMultiCheckBoxWidget):

    def _renderItem(
        self, index, text, value, name, cssClass, checked=False):
        result = super(BadgeInputWidget, self)._renderItem(
            index, text, value, name, cssClass, checked)
        result = result.replace(
            '<label', '<label cms:tooltip="%s"' % escape(text))
        return result


class BadgeDisplayWidget(BadgeInputWidget):

    INPUT = re.compile('<input')

    def _renderItem(self, *args, **kw):
        result = super(BadgeDisplayWidget, self)._renderItem(*args, **kw)
        return self.INPUT.sub('<input disabled="disabled"', result)
