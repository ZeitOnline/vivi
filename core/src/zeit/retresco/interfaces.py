import zope.interface


class ITMS(zope.interface.Interface):
    """The retresco topic management system."""

    def get_keywords(content):
        """Analyzes the given ICMSContent and returns a list of
        zeit.cms.tagging.interfaces.ITag objects."""

    def index(content):
        """Stores the given ICMSContent."""

    def delete_id(uuid):
        """Deletes the document with the given IUUID."""


class TMSError(Exception):
    """Service was unable to process a request because of semantic problems."""


class TechnicalError(Exception):
    """Service had a technical error. The request can be retried."""


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
