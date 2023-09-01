# coding: utf8
from urllib.parse import urlparse
from zeit.cms.i18n import MessageFactory as _
import datetime
import pyramid_dogpile_cache2
import pytz
import re
import zope.app.appsetup.product
import zope.i18nmessageid
import zope.interface
import zope.interface.common.sequence
import zope.schema
import zope.security


DOCUMENT_SCHEMA_NS = 'http://namespaces.zeit.de/CMS/document'
QPS_SCHEMA_NS = 'http://namespaces.zeit.de/QPS/attributes'
ID_NAMESPACE = 'http://xml.zeit.de/'
TEASER_NAMESPACE = 'http://xml.zeit.de/CMS/Teaser'
PRINT_NAMESPACE = 'http://namespaces.zeit.de/CMS/print'
IR_NAMESPACE = 'http://namespaces.zeit.de/CMS/interred'
ZEITWEB_NAMESPACE = 'http://namespaces.zeit.de/CMS/zeit.web'
SPEECHBERT_NAMESPACE = 'http://namespaces.zeit.de/CMS/speech'

# lovely.remotetask stores times as 32 bit leading to an overflow after 2030.
MAX_PUBLISH_DATE = datetime.datetime(2030, 1, 1, tzinfo=pytz.UTC)

# Backward compatibility imports
from zeit.connector.interfaces import (  # noqa
    DeleteProperty, LockingError, IConnector, IResource,
    IWebDAVReadProperties, IWebDAVWriteProperties, IWebDAVProperties)


CONFIG_CACHE = pyramid_dogpile_cache2.get_region('config')
FEATURE_CACHE = pyramid_dogpile_cache2.get_region('feature')


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


class InvalidLinkTarget(zope.schema.ValidationError):
    __doc__ = _('Invalid link target')


def valid_link_target(value):
    if not value:
        return True
    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    if 'invalid-link-targets' not in config:
        return True
    host = urlparse(value).netloc
    for invalid in config['invalid-link-targets'].split(' '):
        if host == invalid:
            raise InvalidLinkTarget()
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
        title='Unique identifier for this type')

    # XXX add other attributes


class IResult(zope.interface.common.sequence.IReadSequence):
    """A list of dicts, with info about the total number of entries."""

    hits = zope.interface.Attribute(
        'Number of total available entries (for pagination)')


@zope.interface.implementer(IResult)
class Result(list):
    """A list with additional property ``hits``."""

    hits = 0


class ITracer(zope.interface.Interface):
    """Wrapper around opentelemetry.trace.Tracer, see there for the full
    method signatures and usage."""

    def start_span(name, attributes=None):
        pass

    def start_as_current_span(name, attributes=None):
        pass


def normalize_filename(filename):
    # NOTE: The master version of the algorithm is implemented in JS in
    # zeit.cms.browser.js:filename.js, keep in sync!
    f = filename
    f = f.strip().lower()
    f = f.replace('ä', 'ae')
    f = f.replace('ö', 'oe')
    f = f.replace('ü', 'ue')
    f = f.replace('ß', 'ss')

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
