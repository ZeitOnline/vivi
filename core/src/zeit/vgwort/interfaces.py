# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.schema


class ITokens(zope.interface.Interface):
    """Provde access to count tokens (Zählmarke)"""

    def claim():
        """Get a (public token, private token) tuple.

        Raises ValueError when there are no tokens.

        """

    def load(csv_file):
        """Load tokens from csv file (file like object)."""

    def add(public_token, private_token):
        """Add tokens."""

    def order(amount):
        """Order new tokens (from the VGWort web service)."""


class IToken(zope.interface.Interface):

    public_token = zope.schema.TextLine(
        title=_('Public VGWort token'),
        required=False)

    private_token = zope.schema.TextLine(
        title=_('Private VGWort token'),
        required=False)


class IReportInfo(zope.interface.Interface):

    reported_on = zope.schema.Datetime(
        title=_(
            'Timestamp when the content object was reported to VGWort'),
        required=False)

    reported_error = zope.schema.Text(
        title=_('Error message that occured while reporting'),
        required=False)


class IGenerallyReportableContent(zope.interface.Interface):
    """Marker for types which are generally reportable to vgwort.

    This marker is used to determine types which content types contain content
    which is in general reportable to vgwort (meldefähig). There are more
    constraints which are not supported yet (≥1800 characters etc.)

    """


class IPixelService(zope.interface.Interface):

    def order_pixels(amount):
        """orders ``amount`` new tokens."""


class IMessageService(zope.interface.Interface):

    def new_document(content):
        """notify VGWort about a published document.

        We do not validate the properties of the content object ourselves (are
        the fields we need filled out, are the length constraints satisfied,
        etc.), but leave that to the web service and report its errors instead.
        """


class WebServiceError(Exception):
    """A VGWort web service was unable to process a request because of semantic
    problems.
    """


class TechnicalError(Exception):
    """A VGWort web service had a technical error.
    The request should be retried again later on.
    """


class IReportableContentSource(zope.interface.Interface):

    def __iter__():
        """returns content objects that are eligble for reporting to VGWort
        but have not been reported yet.
        """

    def mark_done(content):
        """marks the content object as reported to VGWort."""

    def mark_error(content, message):
        """store that the object encountered a semantic error while reporting
        to VGWort.
        """
