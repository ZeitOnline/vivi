import grokcore.component as grok
import zeit.retresco.interfaces
import zope.component
import zope.schema.interfaces


class JSONType(grok.Adapter):
    """Type converter for a json-native datatype."""

    grok.implements(zeit.retresco.interfaces.IDAVPropertyConverter)
    grok.baseclass()

    def fromProperty(self, value):
        return value

    def toProperty(self, value):
        return value


class Bool(JSONType):

    grok.context(zope.schema.interfaces.IBool)


class Int(JSONType):

    grok.context(zope.schema.interfaces.IInt)


@grok.adapter(zope.schema.interfaces.ICollection)
@grok.implementer(zeit.retresco.interfaces.IDAVPropertyConverter)
def Collection(context):
    return zope.component.queryMultiAdapter(
        (context, context.value_type),
        zeit.retresco.interfaces.IDAVPropertyConverter)


class CollectionTextLine(grok.MultiAdapter):

    grok.adapts(
        zope.schema.interfaces.ICollection,
        zope.schema.interfaces.ITextLine)
    grok.implements(zeit.retresco.interfaces.IDAVPropertyConverter)

    # Taken from zeit.cms.content.dav.CollectionTextLineProperty
    def __init__(self, context, value_type):
        self.context = context
        self.value_type = value_type
        self._type = context._type
        if isinstance(self._type, tuple):
            # XXX this is way hacky
            self._type = self._type[0]

    def fromProperty(self, value):
        typ = zeit.cms.content.interfaces.IDAVPropertyConverter(
            self.value_type)
        return self._type([typ.fromProperty(x) for x in value])

    def toProperty(self, value):
        typ = zeit.cms.content.interfaces.IDAVPropertyConverter(
            self.value_type)
        return [typ.toProperty(x) for x in value]


class CollectionChoice(CollectionTextLine):

    grok.adapts(
        zope.schema.interfaces.ICollection,
        zope.schema.interfaces.IChoice)
