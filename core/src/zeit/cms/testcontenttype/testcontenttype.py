import zope.interface

import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.cms.testcontenttype.interfaces
import zeit.cms.type


@zope.interface.implementer(
    zeit.cms.testcontenttype.interfaces.IExampleContentType, zeit.cms.interfaces.IEditorialContent
)
class ExampleContentType(zeit.cms.content.metadata.CommonMetadata):
    """A type for testing."""

    default_template = '<testtype><head/><body/></testtype>'


class ExampleContentTypeType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = ExampleContentType
    interface = zeit.cms.testcontenttype.interfaces.IExampleContentType
    type = 'testcontenttype'
    register_as_type = False
