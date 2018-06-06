from datetime import datetime
from zeit.cms.interfaces import ITypeDeclaration
from zeit.cms.workflow.interfaces import IPublicationStatus
from zeit.content.image.interfaces import IImageMetadata
import grokcore.component as grok
import logging
import lxml.builder
import lxml.etree
import pytz
import zeit.cms.browser.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.content.author.interfaces
import zeit.content.image.interfaces
import zeit.content.link.interfaces
import zeit.content.volume.interfaces
import zeit.retresco.content
import zeit.retresco.interfaces
import zope.component
import zope.interface
import zope.publisher.browser

log = logging.getLogger(__name__)
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

    def __call__(self):
        return {'payload': {}}


class CMSContent(Converter):

    interface = zeit.cms.interfaces.ICMSContent
    grok.name(interface.__name__)

    def __call__(self):
        result = {
            'doc_id': zeit.cms.content.interfaces.IUUID(self.context).id,
            'url': self.context.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE, '/'),
            'doc_type': getattr(ITypeDeclaration(self.context, None),
                                'type_identifier', 'unknown'),
            'body': lxml.etree.tostring(
                zeit.retresco.interfaces.IBody(self.context)),
        }
        result['payload'] = self.collect_dav_properties()
        return result

    DUMMY_ES_PROPERTIES = zeit.retresco.content.WebDAVProperties(None)

    def collect_dav_properties(self):
        result = {}
        properties = zeit.cms.interfaces.IWebDAVReadProperties(self.context)
        for (name, ns), value in properties.items():
            if ns is None:
                ns = ''
            if not ns.startswith(zeit.retresco.interfaces.DAV_NAMESPACE_BASE):
                continue

            field = None
            prop = zeit.cms.content.dav.PROPERTY_REGISTRY.get((name, ns))
            if prop is not None:
                field = prop.field
                field = field.bind(self.context)

            converter = zope.component.queryMultiAdapter(
                (field, self.DUMMY_ES_PROPERTIES),
                zeit.cms.content.interfaces.IDAVPropertyConverter)
            # Only perform type conversion if we have a json-specific one.
            if converter.__class__.__module__ == 'zeit.retresco.content':
                try:
                    davconverter = zope.component.getMultiAdapter(
                        (field, properties),
                        zeit.cms.content.interfaces.IDAVPropertyConverter)
                    pyval = davconverter.fromProperty(value)
                    value = converter.toProperty(pyval)
                except Exception, e:
                    log.warning(
                        'Could not parse DAV property value %r for '
                        '%s.%s at %s [%s: %r]. Using default %r instead.' % (
                            value, ns, name, self.context.uniqueId,
                            e.__class__.__name__, e.args, field.default))
                    value = field.default
            if value is None or value == '':
                # DAVProperty.__set__ has None -> DeleteProperty.
                # Also, elasticsearch rejects '' in date fields.
                continue
            ns, name = zeit.retresco.content.davproperty_to_es(ns, name)
            result.setdefault(ns, {})[name] = value
        return result


class CommonMetadata(Converter):

    interface = zeit.cms.content.interfaces.ICommonMetadata
    grok.name(interface.__name__)

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
        for typ in zeit.retresco.interfaces.ENTITY_TYPES:
            result['rtr_{}s'.format(typ)] = []
        for kw in self.context.keywords:
            key = 'rtr_{}s'.format(self.entity_types.get(
                kw.entity_type, 'keyword'))
            result[key].append(kw.label)

        result['payload'] = {}
        result['payload']['head'] = {
            'authors': [x.target.uniqueId for x in self.context.authorships],
        }
        result['payload']['body'] = {
            'supertitle': self.context.supertitle,
            'title': self.context.title,
            'subtitle': self.context.subtitle,
            'byline': self.context.byline,
        }
        result['payload']['teaser'] = {
            'supertitle': self.context.teaserSupertitle,
            'title': self.context.teaserTitle,
            'text': self.context.teaserText,
        }
        for ns in ['body', 'teaser']:
            data = result['payload'][ns]
            remove_none = []
            for key, value in data.items():
                if value is None:
                    remove_none.append(key)
            for key in remove_none:
                del data[key]
        return result


class PublishInfo(Converter):

    interface = zeit.cms.workflow.interfaces.IPublishInfo
    grok.name(interface.__name__)

    def __call__(self):
        tms_date = self.context.date_last_published_semantic
        if not tms_date:
            tms_date = self.context.date_first_released
        # This field is required by TMS, so always fill with *something*.
        if not tms_date:
            tms_date = MIN_DATE
        return {
            # TMS insists on this precise date format, instead of supporting
            # general ISO8601, sigh.
            'date': tms_date.astimezone(pytz.UTC).strftime(
                '%Y-%m-%dT%H:%M:%SZ'),
        }


class ImageReference(Converter):

    interface = zeit.content.image.interfaces.IImages
    grok.name(interface.__name__)

    def __call__(self):
        image = self.context.image
        if image is None:
            return {}
        result = {
            'teaser_img_url': image.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE, '/'),
            'teaser_img_subline': IImageMetadata(image).caption,
            'payload': {'head': {
                'teaser_image': image.uniqueId,
            }}
        }
        if self.context.fill_color:
            result['payload']['head'][
                'teaser_image_fill_color'] = self.context.fill_color
        return result


class Author(Converter):

    interface = zeit.content.author.interfaces.IAuthor
    grok.name(interface.__name__)

    def __call__(self):
        xml = {}
        for name in dir(zeit.content.author.author.Author):
            prop = getattr(zeit.content.author.author.Author, name)
            if isinstance(prop, zeit.cms.content.property.ObjectPathProperty):
                value = getattr(self.context, name)
                if value:
                    xml[name] = value
        return {
            'title': self.context.display_name,
            'teaser': self.context.summary or self.context.display_name,
            'payload': {'xml': xml}
        }


class Link(Converter):

    interface = zeit.content.link.interfaces.ILink
    grok.name(interface.__name__)

    def __call__(self):
        return {
            'title': self.context.url,
            'teaser': self.context.url,
            'payload': {'body': {
                'url': self.context.url,
                'target': self.context.target,
                'nofollow': self.context.nofollow,
            }}
        }


class Image(Converter):

    interface = zeit.content.image.interfaces.IImageMetadata
    grok.name(interface.__name__)

    def __call__(self):
        title = self.context.title or self.content.__name__
        return {
            # Required fields, so make sure to always index (for zeit.find).
            'title': title,
            'teaser': self.context.caption or title,
        }


class Volume(Converter):
    """This adapter is for indexing actual IVolume objects. Since ICMSContent
    objects can be adapted to IVolume (finding the associated volume object),
    we explicitly restrict this here (which is different from the baseclass).
    """

    interface = zeit.content.volume.interfaces.IVolume
    grok.name(interface.__name__)

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
        }
        covers = [{
            'id': x.get('id'),
            'product_id': x.get('product_id'),
            'href': x.get('href')} for x in self.context.xml.xpath(
                '//covers/cover')]
        if covers:
            result['payload'] = {'head': {'covers': covers}}
        return result


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

        return {'payload': {'vivi': {
            'cms_icon': icon_url,
            'cms_preview_url': preview_url,
            'publish_status': IPublicationStatus(self.content).published,
        }}}


class AccessCounter(Converter):
    # For zeit.find

    interface = zeit.cms.content.interfaces.IAccessCounter
    grok.name(interface.__name__)

    def __call__(self):
        hits = self.context.total_hits
        if hits and self.context.hits:
            hits -= self.context.hits
        return {'payload': {'vivi': {
            'range': hits,
            'range_details': self.context.detail_url,
        }}}


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
