from zeit.cms.content.property import SwitchableProperty
from zeit.connector.interfaces import ISQLMigrate
import grokcore.component as grok
import lxml.builder
import lxml.etree
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.content.author.interfaces
import zeit.content.link.interfaces
import zeit.content.video.interfaces
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


class Link(CommonMetadata):

    interface = zeit.content.link.interfaces.ILink
    grok.name(interface.__name__)


class References(Converter):

    interface = zeit.cms.content.interfaces.ICommonMetadata
    grok.name(interface.__name__ + '.references')

    PROPERTIES = {
        '//head/author': 'authorships',
        '//head/agency': 'agencies',
        '//head/image': 'image',
        '//head/references/reference': 'related',
        '//head/nextread/reference': 'nextread',
    }

    def __call__(self):
        props = zeit.connector.interfaces.IWebDAVProperties(self.content)
        for xpath, name in self.PROPERTIES.items():
            refs = self.content.xml.xpath(xpath)
            if not refs:
                continue
            value = lxml.builder.E.val()
            path = lxml.objectify.ObjectPath(
                xpath.replace('//', '/').replace('/', '.'))
            path.setattr(value, refs)
            value = lxml.etree.tostring(value, encoding=str)
            props[(name, 'http://namespaces.zeit.de/CMS/document')] = value

            path.setattr(self.content.xml, ())
        return True


class AuthorImage(References):

    interface = zeit.content.author.interfaces.IAuthor
    grok.name(interface.__name__ + '.references')
    PROPERTIES = {'//image_group': 'image'}


class VideoImage(References):

    interface = zeit.content.video.interfaces.IVideo
    grok.name(interface.__name__ + '.references')
    PROPERTIES = {'//video_still': 'image'}
