from datetime import datetime
from zeit.cms.interfaces import ITypeDeclaration
from zeit.cms.workflow.interfaces import IModified, IPublicationStatus
from zeit.content.image.interfaces import IImageMetadata
import grokcore.component as grok
import lxml.builder
import lxml.etree
import pytz
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.content.author.interfaces
import zeit.retresco.interfaces
import zope.component
import zope.interface
import zope.publisher.browser

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
    # `TMSRepresentation`, e.g. by specifying `grok.name(interface.__name__)`

    def __new__(cls, context):
        adapted = cls.interface(context, None)
        if adapted is None:
            return None
        instance = super(Converter, cls).__new__(cls, None)
        instance.context = adapted
        instance.content = context
        return instance

    def __init__(self, context):
        pass  # self.context has been set by __new__() already.

    # Maps CMS name -> TMS name. If no TMS name is given, the CMS name is used.
    properties = {}

    def __call__(self):
        return self._copy_properties({'payload': {}})

    def _copy_properties(self, result):
        for src, dst in self.properties.items():
            result['payload'][dst or src] = getattr(self.context, src)
        return result


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

    properties = {
        'commentsAllowed': 'allow_comments',
        'lead_candidate': '',
        'page': '',
        'printRessort': 'print_ressort',
        'push_news': '',
        'ressort': '',
        'sub_ressort': '',
        'subtitle': '',
        'supertitle': '',
        'teaserText': 'teaser_text',
        'teaserTitle': 'teaser_title',
        'teaserSupertitle': 'teaser_supertitle',
        'title': '',
        'tldr_date': '',
        'volume': '',
        'year': '',
    }

    def __call__(self):
        result = {
            'title': self.context.title,
            'supertitle': self.context.supertitle,
            'teaser': self.context.teaserText,
            'section': self.context.ressort,
            # Only for display in TMS UI.
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

        result['payload'] = {
            'authors': [x.target.uniqueId for x in self.context.authorships],
            'author_names': [x.target.display_name
                             for x in self.context.authorships],
            'channels': [' '.join(x) for x in self.context.channels],
            'product_id': self.context.product and self.context.product.id,
            'serie': self.context.serie and self.context.serie.serienname,
            'storystreams': [x.uniqueId for x in self.context.storystreams],
        }
        self._copy_properties(result)
        return result


class PublishInfo(Converter):

    interface = zeit.cms.workflow.interfaces.IPublishInfo
    grok.name(interface.__name__)

    properties = {
        'date_first_released': '',
        'date_last_published': '',
        'date_last_published_semantic': '',
        'published': '',
    }

    def __call__(self):
        lsc = zeit.cms.content.interfaces.ISemanticChange(
            self.content).last_semantic_change
        tms_date = self.context.date_first_released
        if not tms_date:
            tms_date = lsc
        davprops = zeit.cms.interfaces.IWebDAVReadProperties(self.content)
        result = {
            # Required field, but we only use it for display in the TMS UI.
            'date': tms_date or MIN_DATE,
            'payload': {
                'date_last_modified': IModified(
                    self.content).date_last_modified,
                'date_last_semantic_change': lsc,
                # Not mapped in Python code anywhere.
                'date_published_print': davprops.get(
                    ('erscheint', zeit.cms.interfaces.DOCUMENT_SCHEMA_NS)) or
                None,
            }
        }
        self._copy_properties(result)
        return result


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
            'payload': {
                'teaser_image': image.uniqueId,
                'teaser_image_fill_color': self.context.fill_color,
            }
        }


class Article(Converter):

    interface = zeit.content.article.interfaces.IArticle
    grok.name(interface.__name__)

    properties = {
        'is_instant_article': '',
        'is_amp': '',
    }


class BreakingNews(Converter):

    interface = zeit.content.article.interfaces.IBreakingNews
    grok.name(interface.__name__)

    properties = {
        'is_breaking': '',
    }


class Author(Converter):

    interface = zeit.content.author.interfaces.IAuthor
    grok.name(interface.__name__)

    properties = {
        'firstname': '',
        'display_name': '',
        'lastname': '',
    }


class CMSSearch(Converter):
    # For zeit.find

    interface = zeit.cms.interfaces.ICMSContent
    grok.name('zeit.find')

    DUMMY_REQUEST = zope.publisher.browser.TestRequest(
        skin=zeit.cms.browser.interfaces.ICMSSkin)
    SERVER_URL = DUMMY_REQUEST['SERVER_URL']

    def __call__(self):
        icon = zope.component.queryMultiAdapter(
            (self.context, self.DUMMY_REQUEST), name='zmi_icon')
        icon_url = icon and icon.url().replace(self.SERVER_URL, '')

        preview = zope.component.queryMultiAdapter(
            (self.context, self.DUMMY_REQUEST), name='thumbnail')
        try:
            preview_url = zope.component.getMultiAdapter(
                (preview, self.DUMMY_REQUEST),
                zope.traversing.browser.interfaces.IAbsoluteURL)
            preview_url = preview_url()
            preview_url = preview_url.replace(self.SERVER_URL, '')
        except TypeError:
            preview_url = None

        return {'payload': {
            'cms_icon': icon_url,
            'cms_preview_url': preview_url,
            'publish_status': IPublicationStatus(self.content).published,
        }}


class AccessCounter(Converter):
    # For zeit.find

    interface = zeit.cms.content.interfaces.IAccessCounter
    grok.name(interface.__name__)

    def __call__(self):
        hits = self.context.total_hits
        if hits and self.context.hits:
            hits -= self.context.hits
        return {'payload': {
            'range': hits,
            'range_details': self.context.detail_url,
        }}


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
