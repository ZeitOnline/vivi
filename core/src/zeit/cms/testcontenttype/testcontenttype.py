
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.cms.testcontenttype.interfaces
import zeit.cms.type
import zope.interface


class TestContentType(zeit.cms.content.metadata.CommonMetadata):
    """A type for testing."""

    zope.interface.implements(
        zeit.cms.testcontenttype.interfaces.ITestContentType,
        zeit.cms.interfaces.IEditorialContent)

    default_template = (
        '<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
        '<head/><body/></testtype>')


class TestContentTypeType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = TestContentType
    interface = zeit.cms.testcontenttype.interfaces.ITestContentType
    type = 'testcontenttype'
    register_as_type = False
