import zope.interface
import zope.interface.common.sequence


class ITMS(zope.interface.Interface):
    """The retresco topic management system."""

    def get_keywords(content):
        """Analyzes the given ICMSContent and returns a list of
        zeit.cms.tagging.interfaces.ITag objects."""

    def index(content):
        """Stores the given ICMSContent."""

    def delete_id(uuid):
        """Deletes the document with the given IUUID."""

    def get_topicpage_documents(id, start=0, rows=25):
        """Returns an IResult, which is the content contained in the given
        TMS topic page.

        Parameters for pagination are:
        `start`: offset the result by this many entries
        `rows`: return this many entries (i.e. items per page)
        """


class IResult(zope.interface.common.sequence.IReadSequence):
    """A list of dicts with the following keys:

    uniqueId: zeit.cms.interfaces.ICMSContent.uniqueId
    type: zeit.cms.interfaces.ITypeDeclaration.type_identifier
    doc_id: zeit.cms.content.interfaces.IUUID.id
    rtr_keywords, rtr_locations etc.
    plus all keys that ITMSRepresentation puts into `payload`
    """

    hits = zope.interface.Attribute(
        'Number of total available entries (for pagination)')


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


ENTITY_TYPES = (
    'person',
    'location',
    'organisation',
    'product',
    'event',
    'keyword',
)
