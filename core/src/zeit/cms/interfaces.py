# coding: utf8
from zeit.cms.i18n import MessageFactory as _
import datetime
import pytz
import re
import zope.app.container.interfaces
import zope.i18nmessageid
import zope.interface
import zope.interface.common.sequence
import zope.schema
import zope.security


DOCUMENT_SCHEMA_NS = u"http://namespaces.zeit.de/CMS/document"
QPS_SCHEMA_NS = u"http://namespaces.zeit.de/QPS/attributes"
ID_NAMESPACE = u'http://xml.zeit.de/'
TEASER_NAMESPACE = u'http://xml.zeit.de/CMS/Teaser'
PRINT_NAMESPACE = u"http://namespaces.zeit.de/CMS/print"

# lovely.remotetask stores times as 32 bit leading to an overflow after 2030.
MAX_PUBLISH_DATE = datetime.datetime(2030, 1, 1, tzinfo=pytz.UTC)

# Backward compatibility imports
from zeit.connector.interfaces import (
    DeleteProperty, LockingError, IConnector, IResource,
    IWebDAVReadProperties, IWebDAVWriteProperties, IWebDAVProperties)


class ICMSContentType(zope.interface.interfaces.IInterface):
    """Interface for content types."""


class InvalidName(zope.schema.ValidationError):
    __doc__ = _('Name contains invalid characters')


class ValidationError(zope.schema.ValidationError):

    def doc(self):
        return self.args[0]


valid_name_regex = re.compile(r'^[A-Za-z0-9\.\,\-_*()~]+$').match


def valid_name(value):
    if not valid_name_regex(value):
        raise InvalidName(value)
    return True


class ICMSContent(zope.interface.Interface):
    """Interface for all CMS content being loaded from the repository.

    """

    uniqueId = zope.interface.Attribute("Unique Id")

    __name__ = zope.schema.TextLine(
        title=_("File name"),
        readonly=True,
        constraint=valid_name)


class ICMSWCContent(zope.interface.Interface):
    """Adapting to this yields ICMSContent from the workingcopy if present,
    else from the repository."""


class IEditorialContent(ICMSContent):
    """Editorial content.

    Editorial content is content which actually *is* content. That is in
    contrast to for example folders which are used for structuring.

    """


class IAsset(ICMSContent):
    """Assets are special, usually simple, content objects.

    Assets are useles themselves but are integrated into other objects.
    An example is the image.

    """


class IEditPermission(zope.security.interfaces.IPermission):
    """A permission which is always forbidden in the repository."""


class ITypeDeclaration(zope.interface.Interface):

    type_identifier = zope.schema.TextLine(
        title=u'Unique identifier for this type')

    # XXX add other attributes


class IResult(zope.interface.common.sequence.IReadSequence):
    """A list of dicts, with info about the total number of entries."""

    hits = zope.interface.Attribute(
        'Number of total available entries (for pagination)')


def normalize_filename(filename):
    # NOTE: The master version of the algorithm is implemented in JS in
    # zeit.cms.browser.js:filename.js, keep in sync!
    f = filename
    f = f.strip().lower()
    f = f.replace(u'ä', 'ae')
    f = f.replace(u'ö', 'oe')
    f = f.replace(u'ü', 'ue')
    f = f.replace(u'ß', 'ss')

    # Remove special characters at beginning and end
    # XXX It's unclear why this doesn't work as a single regexp.
    f = re.sub('^([^a-z0-9]+)(.*?)$', r'\2', f)
    f = re.sub('^(.*?)([^a-z0-9]+)$', r'\1', f)

    # Replace special characters, but keep dots for special treatment
    f = re.sub('[^a-z0-9.]', '-', f)
    # Save dot of filename extensions
    f = re.sub(
        r'^(.*)\.(jpg|jpeg|png|pdf|mp3|swf|rtf|gif|svg|bmp)$', r'\1_\2', f)
    # Remove all dots
    f = f.replace('.', '-')
    # Restore saved dot
    f = f.replace('_', '.')

    # Collapse multiple consecutive dashes
    f = re.sub('-+', '-', f)

    # Edge case: Remove special char before the filename extension
    f = f.replace('-.', '.')

    return f
