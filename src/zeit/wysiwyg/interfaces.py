# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface

import zc.form.field

from zeit.cms.i18n import MessageFactory as _


class IHTMLContent(zope.interface.Interface):
    """HTML content."""

    html = zc.form.field.HTMLSnippet(title=_("Text"),
                                     required=False)


class IHTMLConverter(zope.interface.Interface):
    """A html converter converts xml to/from html."""

    def to_html(tree):
        """Convert `tree` to html."""

    def from_html(tree, value):
        """Convert `value` to xml replacing data in `tree`."""


class IConversionStep(zope.interface.Interface):

    weight = zope.interface.Attribute(
        "determines the ordering of all ConversionSteps.")

    def to_html(node):
        pass

    def from_html(node):
        pass
