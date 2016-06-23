from datetime import datetime
from zeit.cms.interfaces import ITypeDeclaration
from zeit.content.image.interfaces import IImageMetadata
import grokcore.component as grok
import lxml.builder
import lxml.etree
import pytz
import zeit.cms.content.interfaces
import zeit.cms.workflow.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.retresco.interfaces
import zope.component
import zope.interface

MIN_DATE = datetime(1970, 1, 1, tzinfo=pytz.UTC)


class TMSRepresentation(grok.Adapter):

    grok.context(zeit.cms.interfaces.ICMSContent)
    grok.implements(zeit.retresco.interfaces.ITMSRepresentation)

    def __call__(self):
        result = {}
        for name, converter in sorted(zope.component.getAdapters(
                (self.context,), zeit.retresco.interfaces.ITMSRepresentation)):
            if not name:
                # The unnamed adapter is the one which runs all the named
                # adapters, i.e. this one.
                continue
            merge(converter(), result)
        return result


class Converter(grok.Adapter):
    """This adapter works a bit differently: It adapts its context to a
    separately _configured_ `interface`, and declines if that is not possible;
    but all adapters are _registered_ for the same basic ICMSContent interface.
    This way we can retrieve data stored in various DAVPropertyAdapters.
    """

    grok.baseclass()
    grok.context(zeit.cms.interfaces.ICMSContent)
    grok.implements(zeit.retresco.interfaces.ITMSRepresentation)

    interface = NotImplemented
    # Subclasses need to register as named adapters to work with
    # TMSRepresentation, e.g. by specifying `grok.name(interface.__name__)`

    def __new__(cls, context):
        context = cls.interface(context, None)
        if context is None:
            return None
        instance = super(Converter, cls).__new__(cls, context)
        instance.context = context
        return instance

    def __init__(self, context):
        pass  # self.context has been set by __new__() already.

    def __call__(self):
        return {}


class CMSContent(Converter):

    interface = zeit.cms.interfaces.ICMSContent
    grok.name(interface.__name__)

    def __call__(self):
        return {
            'doc_id': zeit.cms.content.interfaces.IUUID(self.context).id,
            'url': self.context.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE, '/'),
            'doc_type': getattr(ITypeDeclaration(self.context, None),
                                'type_identifier', 'unknown'),
            'body': lxml.etree.tostring(
                zeit.retresco.interfaces.IBody(self.context)),
        }


class CommonMetadata(Converter):

    interface = zeit.cms.content.interfaces.ICommonMetadata
    grok.name(interface.__name__)

    def __call__(self):
        result = {
            'title': self.context.title,
            'supertitle': self.context.supertitle,
            'teaser': self.context.teaserText,
            'section': self.context.ressort,
            'author': ', '.join([
                x.target.display_name for x in self.context.authorships])
        }
        for typ in zeit.retresco.interfaces.ENTITY_TYPES:
            result['rtr_{}s'.format(typ)] = []
        for kw in self.context.keywords:
            key = 'rtr_{}s'.format(kw.entity_type)
            # We might still encounter keywords from the old zeit.intrafind
            # with incompatible entity_types, so be extra defensive.
            if key in result:
                result[key].append(kw.label)
        return result


class PublishInfo(Converter):

    interface = zeit.cms.workflow.interfaces.IPublishInfo
    grok.name(interface.__name__)

    def __call__(self):
        return {
            # XXX date is required; what about unpublished content?
            'date': self.context.date_first_released or MIN_DATE
        }


class ImageReference(Converter):

    interface = zeit.content.image.interfaces.IImages
    grok.name(interface.__name__)

    def __call__(self):
        image = self.context.image
        if image is None:
            return {}
        return {
            'teaser_img_url': image.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE, '/'),
            'teaser_img_subline': IImageMetadata(image).caption,
        }


@grok.adapter(zope.interface.Interface)
@grok.implementer(zeit.retresco.interfaces.IBody)
def body_default(context):
    return lxml.builder.E.body()


@grok.adapter(zeit.cms.content.interfaces.IXMLRepresentation)
@grok.implementer(zeit.retresco.interfaces.IBody)
def body_xml(context):
    # This is probably not very helpful.
    return context.xml


@grok.adapter(zeit.content.article.interfaces.IArticle)
@grok.implementer(zeit.retresco.interfaces.IBody)
def body_article(context):
    return context.xml.body


def merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value
    return destination
