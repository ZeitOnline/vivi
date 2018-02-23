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
import zeit.content.gallery.interfaces
import zeit.content.volume.interfaces
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
        if not self._validate(result):
            return None
        return result

    REQUIRED_FIELDS = (
        'doc_id', 'title', 'teaser',
        # For completeness, but these cannot be empty with our implementation.
        'doc_type', 'url', 'date',
    )

    def _validate(self, data):
        return all([data.get(x) for x in self.REQUIRED_FIELDS])


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
        'access': '',
        'commentsAllowed': 'allow_comments',
        'commentSectionEnable': 'show_comments',
        'lead_candidate': '',
        'page': '',
        'printRessort': 'print_ressort',
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

    entity_types = {
        # BBB map zeit.intrafind entity_type to retresco.
        'Person': 'person',
        'Location': 'location',
        'Organization': 'organisation',
        'free': 'keyword',
    }
    entity_types.update({x: x for x in zeit.retresco.interfaces.ENTITY_TYPES})

    def __call__(self):
        section = None
        if self.context.ressort:
            section = u'/' + self.context.ressort
            if self.context.sub_ressort:
                section += u'/' + self.context.sub_ressort
        result = {
            'title': self.context.title,
            'supertitle': self.context.supertitle,
            'teaser': self.context.teaserText or self.context.title,
            'section': section,
            # Only for display in TMS UI.
            'author': u', '.join(
                [x.target.display_name for x in self.context.authorships] or
                [x for x in self.context.authors if x])
        }
        # XXX should simply be self.context.keywords, but for transitional
        # period we explicitly need to get the Retresco ones, otherwise
        # production will index the Intrafind ones to TMS.
        try:
            keywords = list(zeit.retresco.tagger.Tagger(self.context).values())
        except Exception:
            keywords = ()
        for typ in zeit.retresco.interfaces.ENTITY_TYPES:
            result['rtr_{}s'.format(typ)] = []
        for kw in keywords:
            key = 'rtr_{}s'.format(self.entity_types.get(
                kw.entity_type, 'keyword'))
            result[key].append(kw.label)

        result['payload'] = {
            'authors': [x.target.uniqueId for x in self.context.authorships],
            'author_names': [
                x.target.display_name for x in self.context.authorships] or [
                    # BBB for content without author object references.
                    x for x in self.context.authors if x],
            'channels': [' '.join([x for x in channel if x])
                         for channel in self.context.channels],
            'keywords': [{'label': x.label, 'entity_type': x.entity_type,
                          'pinned': x.pinned} for x in keywords],
            'product_id': self.context.product and self.context.product.id,
            'serie': self.context.serie and self.context.serie.serienname,
            'storystreams': [x.centerpage_id
                             for x in self.context.storystreams],
        }
        return self._copy_properties(result)


class PublishInfo(Converter):

    interface = zeit.cms.workflow.interfaces.IPublishInfo
    grok.name(interface.__name__)

    properties = {
        'date_first_released': '',
        'date_last_published': '',
        'date_last_published_semantic': '',
        'published': '',
        'date_print_published': '',
    }

    def __call__(self):
        lsc = zeit.cms.content.interfaces.ISemanticChange(
            self.content).last_semantic_change
        tms_date = self.context.date_last_published_semantic
        if not tms_date:
            tms_date = self.context.date_first_released
        result = {
            # Required field
            'date': tms_date or MIN_DATE,
            'payload': {
                'date_last_modified': IModified(
                    self.content).date_last_modified,
                'date_last_semantic_change': lsc,
            }
        }
        return self._copy_properties(result)


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
        'genre': 'article_genre',
        'header_layout': 'article_header',
        'is_amp': '',
        'is_instant_article': '',
        'template': 'article_template',
    }


class Author(Converter):

    interface = zeit.content.author.interfaces.IAuthor
    grok.name(interface.__name__)

    properties = {
        'firstname': '',
        'display_name': '',
        'lastname': '',
    }


class BreakingNews(Converter):

    interface = zeit.content.article.interfaces.IBreakingNews
    grok.name(interface.__name__)

    properties = {
        'is_breaking': '',
    }


class CenterPage(Converter):

    interface = zeit.content.cp.interfaces.ICenterPage
    grok.name(interface.__name__)

    properties = {
        'type': 'cp_type',
    }


class Gallery(Converter):

    interface = zeit.content.gallery.interfaces.IGallery
    grok.name(interface.__name__)

    properties = {
        'type': 'gallery_type',
    }


class Volume(Converter):
    """This adapter is for indexing actual IVolume objects. Since ICMSContent
    objects can be adapted to IVolume (finding the associated volume object),
    we explicitly restrict this here (which is different from the baseclass).
    """

    interface = zeit.content.volume.interfaces.IVolume
    grok.name(interface.__name__)

    properties = {
        'date_digital_published': '',
        'volume': '',
        'year': '',
    }

    def __new__(cls, context):
        if not cls.interface.providedBy(context):
            return None
        instance = super(Converter, cls).__new__(cls, None)
        instance.context = context
        instance.content = context
        return instance

    def __call__(self):
        result = {
            'title': self.context.teaserText or 'Ausgabe',
            'teaser': self.context.teaserText or 'Ausgabe',
            'payload': {
                'product_id': self.context.product and self.context.product.id,
            }
        }
        return self._copy_properties(result)


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
