import grokcore.component as grok
import zeit.retresco.interfaces
import zope.component
import zope.schema.interfaces


class Content(object):

    zope.interface.implements(zeit.retresco.interfaces.ITMSContent)

    xml = lxml.objectify.XML('<empty/>')

    def __init__(self, data):
        self._tms_payload = data.get('payload', {})
        self.uniqueId = zeit.cms.interfaces.ID_NAMESPACE + data['url'][1:]
        self.__name__ = os.path.basename(self.uniqueId)


class JSONType(grok.MultiAdapter):
    """Type converter for a json-native datatype."""

    grok.implements(zeit.cms.content.interfaces.IDAVPropertyConverter)
    grok.baseclass()

    def __init__(self, context, content):
        pass

    def fromProperty(self, value):
        return value

    def toProperty(self, value):
        return value


class Bool(JSONType):

    grok.adapts(
        zope.schema.interfaces.IBool,
        zeit.retresco.interfaces.ITMSContent)


class Int(JSONType):

    grok.adapts(
        zope.schema.Int,  # IFromUnicode is parallel to IInt
        zeit.retresco.interfaces.ITMSContent)


class CollectionTextLine(grok.MultiAdapter):

    grok.adapts(
        zope.schema.interfaces.ICollection,
        zope.schema.interfaces.ITextLine,
        zeit.retresco.interfaces.ITMSContent)
    grok.implements(zeit.cms.content.interfaces.IDAVPropertyConverter)

    # Taken from zeit.cms.content.dav.CollectionTextLineProperty
    def __init__(self, context, value_type, content):
        self.context = context
        self.value_type = value_type
        self.content = content
        self._type = context._type
        if isinstance(self._type, tuple):
            # XXX this is way hacky
            self._type = self._type[0]

    def fromProperty(self, value):
        typ = zope.component.getMultiAdapter(
            (self.value_type, self.content),
            zeit.cms.content.interfaces.IDAVPropertyConverter)
        return self._type([typ.fromProperty(x) for x in value])

    def toProperty(self, value):
        typ = zope.component.getMultiAdapter(
            (self.value_type, self.content),
            zeit.cms.content.interfaces.IDAVPropertyConverter)
        return [typ.toProperty(x) for x in value]


class CollectionChoice(CollectionTextLine):

    grok.adapts(
        zope.schema.interfaces.ICollection,
        zope.schema.interfaces.IChoice,
        zeit.retresco.interfaces.ITMSContent)
