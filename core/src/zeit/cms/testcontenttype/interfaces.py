import zeit.cms.content.interfaces
import zeit.cms.tagging.interfaces


class IExampleContentType(
    zeit.cms.content.interfaces.ICommonMetadata, zeit.cms.content.interfaces.IXMLContent
):
    """A type for testing."""

    keywords = zeit.cms.tagging.interfaces.Keywords(required=False, default=())


IExampleContentType.setTaggedValue('zeit.cms.type', 'testcontenttype')
IExampleContentType.setTaggedValue('zeit.cms.addform', 'zeit.cms.testcontenttype.Add')
