from zeit.cms.content.property import SwitchableProperty
from zeit.connector.interfaces import ISQLMigrate
import grokcore.component as grok
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.content.author.interfaces
import zope.component


def migrate(resource):
    content = zeit.cms.interfaces.ICMSContent(resource)
    migrate = zeit.connector.interfaces.ISQLMigrate(content, None)
    if migrate is None:
        return resource
    props = zeit.connector.interfaces.IWebDAVProperties(content)
    # Work around vivi API assumptions about repository/local content.
    props.update(resource.properties)
    if migrate():
        resource = zeit.connector.interfaces.IResource(content)
    return resource


@grok.implementer(ISQLMigrate)
class Migrate(grok.Adapter):

    grok.context(zeit.cms.content.interfaces.IXMLRepresentation)

    def __call__(self):
        changed = False
        for name, converter in sorted(zope.component.getAdapters(
                (self.context,), ISQLMigrate)):
            if not name:
                # The unnamed adapter is the one which runs all the named
                # adapters, i.e. this one.
                continue
            result = converter()
            if not changed:
                changed = result
        return changed


@grok.implementer(ISQLMigrate)
class Converter(grok.Adapter):

    grok.baseclass()
    grok.context(zeit.cms.content.interfaces.IXMLRepresentation)

    interface = NotImplemented

    def __new__(cls, context):
        adapted = cls.interface(context, None)
        if adapted is None:
            return None
        instance = object.__new__(cls)
        instance.context = adapted
        instance.content = context
        return instance

    def __init__(self, context):
        pass  # self.context has been set by __new__() already.

    def __call__(self):
        raise NotImplementedError()


class CommonMetadata(Converter):

    interface = zeit.cms.content.interfaces.ICommonMetadata
    grok.name(interface.__name__)

    def __call__(self):
        cls = type(self.content)
        for name in dir(cls):
            attr = getattr(cls, name, None)
            if not isinstance(attr, SwitchableProperty):
                continue
            value = attr.body.__get__(self.content, cls)
            missing = (
                attr.body.field.missing_value if attr.body.field else None)
            if value != missing:
                attr.meta.__set__(self.content, value)
                attr.body.__set__(self.content, None)
        return True


class Author(CommonMetadata):

    interface = zeit.content.author.interfaces.IAuthor
    grok.name(interface.__name__)
