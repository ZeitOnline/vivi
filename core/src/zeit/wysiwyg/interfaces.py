import zc.form.field
import zope.interface

from zeit.cms.i18n import MessageFactory as _


class IHTMLContent(zope.interface.Interface):
    """HTML content."""

    html = zc.form.field.HTMLSnippet(title=_('Text'), required=False)


class IHTMLConverter(zope.interface.Interface):
    """A html converter converts xml to/from html."""

    storage = zope.interface.Attribute(
        """\
        (Mapping) container that can be used by conversion steps to store
        stuff.
        """
    )

    def to_html(tree):
        """Convert `tree` to html."""

    def from_html(tree, value):
        """Convert `value` to xml replacing data in `tree`."""


class IConversionStep(zope.interface.Interface):
    """Encapsulates one step of XML<-->HTML conversion.
    see zeit.wysiwyg.html.ConversionStep for details."""

    order_to_html = zope.interface.Attribute(
        'determines the ordering of ConversionSteps from XML to HTML.'
    )

    order_to_xml = zope.interface.Attribute(
        'determines the ordering of ConversionSteps from HTML to XML.'
    )

    def to_html(node):
        pass

    def from_html(node):
        pass
