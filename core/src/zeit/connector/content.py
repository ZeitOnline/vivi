from sqlalchemy import Boolean, Column, Unicode
import grokcore.component as grok
import zope.schema

from zeit.connector.resource import PropertyKey
import zeit.cms.content.interfaces


class CommonMetadata:
    access = Column(Unicode, index=True, info={'namespace': 'document', 'name': 'access'})
    overscrolling = Column(
        Boolean, index=True, info={'namespace': 'document', 'name': 'overscrolling'}
    )


@grok.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class SQLType(grok.MultiAdapter):
    """Type converter for a sql-native datatype."""

    grok.baseclass()

    def __init__(self, context, properties, propertykey):
        pass

    def fromProperty(self, value):
        return value

    def toProperty(self, value):
        return value


class Bool(SQLType):
    grok.adapts(
        zope.schema.Bool,  # IFromUnicode is parallel to IBool
        zeit.connector.interfaces.ISQLProperties,
        PropertyKey,
    )
