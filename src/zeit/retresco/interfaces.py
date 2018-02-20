import zeit.cms.interfaces
import zope.interface


ENTITY_TYPES = (
    'person',
    'location',
    'organisation',
    'product',
    'event',
    'keyword',
)

DAV_NAMESPACE_BASE = 'http://namespaces.zeit.de/CMS/'


class ITMS(zope.interface.Interface):
    """The retresco topic management system."""

    def extract_keywords(content):
        """Analyzes the given ICMSContent and returns a list of
        zeit.cms.tagging.interfaces.ITag objects."""

    def index(content, override_body=None):
        """Stores the given ICMSContent.

        Pass override_body to store the result of an enrich-intextlink call.
        """

    def enrich(content, intextlinks=True):
        """Performs TMS analysis ("enrich" and "in_text_links" if given)."""

    def publish(content):
        """Mark content as published in TMS.
        This is normally done by the publisher, not vivi.
        """

    def delete_id(uuid):
        """Deletes the document with the given IUUID."""

    # vivi-internal

    def get_keywords(search_string):
        """Get an iterable of tag objects which match the search string.

        The tag objects provide zeit.cms.tagging.interfaces.ITag.
        """

    def get_locations(search_string):
        """Get an iterable of tag objects which match the search string
        and have entity_type=location.
        """

    def get_article_data(content):
        """Return the data stored in TMS for the given article as a dict,
        unconverted i.e. in TMS format.
        """

    # zeit.web support

    def get_topicpages(start=0, rows=25):
        """Return an IResult containing dicts with topicpage metadata"""

    def get_all_topicpages():
        """Returns an iterable of all available topicpage dicts"""

    def get_topicpage_documents(id, start=0, rows=25):
        """Returns an zeit.cms.interfaces.IResult that contains dicts
        with metadata of the content contained in the given TMS topic page.
        The dicts have the following keys:

        uniqueId: zeit.cms.interfaces.ICMSContent.uniqueId
        doc_type: zeit.cms.interfaces.ITypeDeclaration.type_identifier
        doc_id: zeit.cms.content.interfaces.IUUID.id
        rtr_keywords, rtr_locations etc.
        plus all keys that ITMSRepresentation puts into `payload`

        Parameters for pagination are:
        `start`: offset the result by this many entries
        `rows`: return this many entries (i.e. items per page)
        """

    def get_article_body(uuid, timeout=None):
        """Returns the (in-text-link annotated) article body XML."""

    def get_article_keywords(uuid, timeout=None):
        """Returns a list of ITag objects with an additional property `link`,
        containing a path (without leading slash) to the corresponding
        topicpage. Only keywords that have not already been in-text-linked in
        this article are returned.

        The result is sorted as follows: first pinned keywords, in the order
        set in vivi, then remaining keywords sorted by descending TMS score.
        """


class TMSError(Exception):
    """Service was unable to process a request because of semantic problems."""

    def __init__(self, message, status):
        super(TMSError, self).__init__(message)
        self.status = status


class TechnicalError(Exception):
    """Service had a technical error. The request can be retried."""


class ITMSRepresentation(zope.interface.Interface):
    """Adapts an ICMSContent to a (possibly nested) dict with the TMS fields.

    The toplevel keys are defined by the TMS, while everyting below `payload`
    is defined by us.
    """

    def __call__():
        """Returns the dict (we unfortunately cannot return the dict directly
        from as the adaptation result for mechanical reasons).
        """


class IBody(zope.interface.Interface):
    """Adapts an ICMSContent to an lxml node that represents the "body"
    of the content object, i.e. that contains the fulltext.
    """


class ITMSContent(zeit.cms.interfaces.ICMSContent):
    """Marker interface for content that was resolved from a TMS or
    Elasticsearch query result."""


class IElasticsearch(zope.interface.Interface):
    """Search using the Elasticsearch service."""

    def search(query, sort_order, start=0, rows=25, include_payload=False):
        """Search using `query` and sort by `sort_order`.

        query ... dictionary according to Elasticsearch Query DSL
        start ... offset in the search result.
        rows ... limit number of results.
        include_payload ... mix the `payload` dict into the results

        Returns a `zeit.cms.interfaces.IResult` object, containing dictionaries
        with the keys `uniqueId`, `doc_id` and `doc_type`.
        """
