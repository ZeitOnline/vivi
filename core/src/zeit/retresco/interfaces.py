"""zeit.retresco provides the following key features:

* An implementation of ``zeit.cms.tagging.interfaces.ITagger`` and ``ITag``
  (in .tagger and .tag respectively), and thus a backend for
  ``zeit.cms.content.interfaces.ICommonMetadata.keywords``
* ``ITMS``: Python interface to the Retresco TMS REST API, used by
  ``.tagger.Tagger`` and ``zeit.content.cp.automatic`` to populate
  ``IAutomaticArea`` contents
* ``IElasticsearch``: Python interface for querying elasticsearch, used for
  ``IAutomaticArea`` as well
* Converting ``ICMSContent`` objects to a nested dict structure and back again
  with ``ITMSRepresentation`` and ``ITMSContent``
"""
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
        """Returns an iterable of all available topicpage dicts.

        Note: This is pretty slow, production has >10k topicpages, and we have
        to paginate through all of them. So this is less of a general API you
        should call, its main use case is updating /data/topicpages.xml in a
        cronjob. You should parse that file instead of calling this function in
        almost all cases.
        """

    def get_topicpage_documents(
            id, start=0, rows=25, filter=None, sort_by=None):
        """Returns an zeit.cms.interfaces.IResult that contains dicts
        with metadata of the content contained in the given TMS topic page.
        The dicts have the following keys:

        url: zeit.cms.interfaces.ICMSContent.uniqueId (only the path)
        doc_type: zeit.cms.interfaces.ITypeDeclaration.type_identifier
        doc_id: zeit.cms.content.interfaces.IUUID.id
        rtr_keywords, rtr_locations etc.
        payload: see ITMSRepresentation

        Parameters are:
        `start`: offset the result by this many entries
        `rows`: return this many entries (i.e. items per page)
        `filter`: return filtered entries (i.e. only videos)
        `order`: sort entries by given field (i.e. kpi_comments, ...)
        """

    def get_article_body(content, timeout=None):
        """Returns the (in-text-link annotated) article body XML."""

    def get_article_topiclinks(content, published=False, timeout=None):
        """Returns a list of ITag objects with an additional property `link`,
        containing a path (without leading slash) to the corresponding
        topicpage. Only keywords that have not already been in-text-linked in
        this article are returned.

        The result is sorted as follows: first pinned keywords, in the order
        set in vivi, then remaining keywords sorted by descending TMS score.

        The `published` flag determines, if the keyword lookup is done for
        already published content.
        """

    def get_related_documents(content, rows=15, filter=None):
        """Returns a list of documents that relates to the given uuid
        and filtered by the filtername.
        """

    def get_related_topics(topicpage_id, rows=10):
        """Returns a list of namespaced ids that relate to the given
        topicpage_id.
        """

    def get_content_containing_topicpages(content, supress_errors=False):
        """Returns a list of ITag objects corresponding to the topicpages
        on which the content has been published
        """


class TMSError(Exception):
    """Service was unable to process a request because of semantic problems."""

    def __init__(self, message, status):
        super().__init__(message)
        self.status = status


class TechnicalError(Exception):
    """Service had a technical error. The request can be retried."""

    def __init__(self, message, status):
        super().__init__(message)
        self.status = status


class ITMSRepresentation(zope.interface.Interface):
    """Adapts an ICMSContent to a (possibly nested) dict with the TMS fields.

    The toplevel keys are defined by the TMS, while everything below `payload`
    is defined by us.

    We transform the DAV properties mechanically, i.e.
      (http://namespaces.zeit.de/CMS/document, ressort) ->
        payload/document/ressort
    and then add explicitly picked parts of the XML body, e.g.
    payload/body/title or payload/head/teaser_image.
    """

    def __call__():
        """Returns the dict (we unfortunately cannot return the dict directly
        from as the adaptation result for mechanical reasons).
        """


class IBody(zope.interface.Interface):
    """Adapts an ICMSContent to an lxml node that represents the "body"
    of the content object, i.e. that contains the fulltext.
    """


class ISkipEnrich(zope.interface.Interface):
    """Marker interface to denote ICMSContent that should not be enriched
    automatically.

    Current example: centerpages provide this, because their body contains
    no sensibly enricheable text (it's just control information), and thus
    enriching them only wastes time.
    """


class ITMSContent(zeit.cms.interfaces.ICMSContent):
    """Adapts a TMS or Elasticsearch result dict to an ICMSContent object.

    This is the inverse of ITMSRepresentation. We instantiate the normal
    content type class (Article, CenterPage, etc), and augment it with a
    mixin base class that provides custom IWebDAVProperties (backed by the
    nested payload dict) and reconstructs a minimal XML body from those parts
    explicitly converted by ITMSRepresentation.
    """


class IKPI(zope.interface.Interface):
    """Provides access to kpi fields (visits, comments, etc.) on ITMSContent.
    """

    visits = zope.schema.Int(default=0, readonly=True)
    comments = zope.schema.Int(default=0, readonly=True)
    subscriptions = zope.schema.Int(default=0, readonly=True)


class IElasticDAVProperties(zeit.connector.interfaces.IWebDAVProperties):
    """Marker interface so we can register special IDAVPropertyConverter
    variants for ITMSContent objects.
    """


class IElasticsearch(zope.interface.Interface):
    """Search using the Elasticsearch service."""

    def search(query, sort_order, start=0, rows=25, include_payload=False):
        """Search using `query` and sort by `sort_order`.

        query ... dictionary according to Elasticsearch Query DSL
        start ... offset in the search result.
        rows ... limit number of results.
        include_payload ... add the ITMSRepresentation `payload` dict to
            the results.

        Returns a `zeit.cms.interfaces.IResult` object, containing dictionaries
        with the keys `url`, `doc_id` and `doc_type`.
        """
