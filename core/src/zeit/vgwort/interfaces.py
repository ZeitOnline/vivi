# coding: utf8
import pendulum
import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.connector.search


class SearchVars:
    def SearchVar(name, ns):
        prefix = 'http://namespaces.zeit.de/CMS/'
        return zeit.connector.search.SearchVar(name, prefix + ns)

    PUBLISHED = SearchVar('published', 'workflow')
    FIRST_RELEASED = SearchVar('date_first_released', 'document')
    AUTHOR = SearchVar('author', 'document')
    PRIVATE_TOKEN = SearchVar('private_token', 'vgwort')
    PUBLIC_TOKEN = SearchVar('public_token', 'vgwort')
    REPORTED_ON = SearchVar('reported_on', 'vgwort')
    REPORTED_ERROR = SearchVar('reported_error', 'vgwort')


class ITokens(zope.interface.Interface):
    """Provde access to count tokens (Zählmarke)"""

    def claim():
        """Get a (public token, private token) tuple.

        Raises ValueError when there are no tokens.

        """

    def claim_immediately():
        """Claim a token outside of the current transaction."""

    def load(csv_file):
        """Load tokens from csv file (file like object)."""

    def add(public_token, private_token):
        """Add tokens."""

    def order(amount):
        """Order new tokens (from the VGWort web service)."""


class IToken(zope.interface.Interface):
    public_token = zope.schema.TextLine(title=_('Public VGWort token'), required=False)

    private_token = zope.schema.TextLine(title=_('Private VGWort token'), required=False)


class IReportInfo(zope.interface.Interface):
    reported_on = zope.schema.Datetime(
        title=_('Timestamp when the content object was reported to VGWort'), required=False
    )

    reported_error = zope.schema.Text(
        title=_('Error message that occured while reporting'), required=False
    )


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
        """iteratte over ICMSContent objects that are eligble for reporting

        The iterator does not contain objects which have been reported once.

        """

    def mark_done(content):
        """marks the content object as reported to VGWort."""

    def mark_error(content, message):
        """store that the object encountered a semantic error while reporting
        to VGWort.
        """


def in_daily_maintenance_window():
    # See "METIS Integrationsbeschreibung 3.2.1.1"
    # https://tom.vgwort.de/Documents/pdfs/dokumentation/metis/DOC_Verlagsmeldung.pdf
    now = pendulum.now('Europe/Berlin')
    start = now.replace(hour=2, minute=50, second=0, microsecond=0)
    end = now.replace(hour=8, minute=30, second=0, microsecond=0)
    return start <= now <= end
