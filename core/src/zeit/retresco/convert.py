import itertools
import logging
import os.path
import re

from pendulum import datetime
import grokcore.component as grok
import lxml.builder
import lxml.etree
import pendulum
import zope.component
import zope.interface
import zope.publisher.browser

from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.interfaces import ITypeDeclaration
from zeit.cms.workflow.interfaces import IPublicationStatus
from zeit.connector.interfaces import DeleteProperty
from zeit.connector.resource import PropertyKey
from zeit.content.article.edit.interfaces import IRecipeList
from zeit.content.audio.interfaces import IAudioReferences
from zeit.content.image.interfaces import IImageMetadata
from zeit.retresco.interfaces import DAV_NAMESPACE_BASE
import zeit.cms.browser.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.grok
import zeit.cms.workflow.interfaces
import zeit.content.article.interfaces
import zeit.content.audio.interfaces
import zeit.content.author.interfaces
import zeit.content.dynamicfolder.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.infobox.interfaces
import zeit.content.link.interfaces
import zeit.content.portraitbox.interfaces
import zeit.content.rawxml.interfaces
import zeit.content.text.interfaces
import zeit.content.volume.interfaces
import zeit.push.interfaces
import zeit.retresco.content
import zeit.retresco.interfaces
import zeit.seo.interfaces
import zeit.wochenmarkt.recipe
import zeit.wochenmarkt.sources


log = logging.getLogger(__name__)
MIN_DATE = datetime(1970, 1, 1)


@grok.implementer(zeit.retresco.interfaces.ITMSRepresentation)
class TMSRepresentation(grok.Adapter):
    grok.context(zeit.cms.interfaces.ICMSContent)

    validate = True  # Kludge to enable reuse in zeit.workflow.publish_3rdparty

    def __call__(self):
        result = {}
        for name, converter in sorted(
            zope.component.getAdapters((self.context,), zeit.retresco.interfaces.ITMSRepresentation)
        ):
            if not name:
                # The unnamed adapter is the one which runs all the named
                # adapters, i.e. this one.
                continue
            merge_and_skip_empty(converter(), result)
        if self.validate and not self._is_valid(result):
            return None
        return result

    REQUIRED_FIELDS = (
        'doc_id',
        'title',
        'teaser',
        # For completeness, but these cannot be empty with our implementation.
        'doc_type',
        'url',
        'date',
    )

    def _is_valid(self, data):
        return all(data.get(x) for x in self.REQUIRED_FIELDS)


@grok.implementer(zeit.retresco.interfaces.ITMSRepresentation)
class Converter(zeit.cms.grok.IndirectAdapter):
    grok.baseclass()

    def __call__(self):
        return {'payload': {}}


class CMSContent(Converter):
    interface = zeit.cms.interfaces.ICMSContent
    grok.name(interface.__name__)

    def __call__(self):
        body = zeit.retresco.interfaces.IBody(self.context)
        result = {
            'doc_id': zeit.cms.content.interfaces.IUUID(self.context).id,
            'url': self.context.uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE, '/'),
            'doc_type': getattr(ITypeDeclaration(self.context, None), 'type_identifier', 'unknown'),
            'body': lxml.etree.tostring(body, encoding=str),
        }
        result['payload'] = self.collect_dav_properties()
        result['payload'].setdefault('meta', {})['tms_last_indexed'] = pendulum.now(
            'UTC'
        ).isoformat()
        return result

    DUMMY_ES_PROPERTIES = zeit.retresco.content.WebDAVProperties(None)
    DEPRECATED = {
        ('document', 'amp_code'),
        ('document', 'breaking_news'),
        ('document', 'DailyNL'),
        ('document', 'comments_api_v2'),
        ('document', 'comments_rebrush'),
        ('document', 'countings'),
        ('document', 'export_cds'),
        ('document', 'foldable'),
        ('document', 'is_amp'),
        ('document', 'is_instant_article'),
        ('document', 'lead_candidate'),
        ('document', 'minimal_header'),
        ('document', 'rebrush_website_content'),
        ('document', 'recent_comments_first'),
        ('document', 'storystreams'),
        ('document', 'tldr_date'),
        ('document', 'tldr_milestone'),
        ('document', 'tldr_text'),
        ('document', 'tldr_title'),
    }

    def collect_dav_properties(self):
        result = {}
        properties = zeit.cms.interfaces.IWebDAVReadProperties(self.context)
        for (name, ns), value in properties.items():
            if ns is None:
                ns = ''
            if not ns.startswith(DAV_NAMESPACE_BASE):
                continue
            if (ns.replace(DAV_NAMESPACE_BASE, ''), name) in self.DEPRECATED:
                continue

            field = None
            key = PropertyKey(name, ns)
            prop = zeit.cms.content.dav.PROPERTY_REGISTRY.get(key)
            if prop is not None:
                field = prop.field
                field = field.bind(self.context)

            converter = zope.component.queryMultiAdapter(
                (field, self.DUMMY_ES_PROPERTIES, key),
                zeit.cms.content.interfaces.IDAVPropertyConverter,
            )
            # Only perform type conversion if we have a json-specific one.
            if converter.__class__.__module__ == 'zeit.retresco.content':
                try:
                    davconverter = zope.component.getMultiAdapter(
                        (field, properties, key), zeit.cms.content.interfaces.IDAVPropertyConverter
                    )
                    pyval = davconverter.fromProperty(value)
                    value = converter.toProperty(pyval)
                except Exception as e:
                    log.warning(
                        'Could not parse DAV property value %r for '
                        '%s.%s at %s [%s: %r]. Using default %r instead.'
                        % (
                            value,
                            ns,
                            name,
                            self.context.uniqueId,
                            e.__class__.__name__,
                            e.args,
                            field.default,
                        )
                    )
                    value = field.default
            if value is None or value is DeleteProperty or value == '':
                # DAVProperty.__set__ has None -> DeleteProperty.
                # Also, elasticsearch rejects '' in date fields.
                continue
            ns, name = zeit.retresco.content.davproperty_to_es(ns, name)
            result.setdefault(ns, {})[name] = value
        return result


class CommonMetadata(Converter):
    interface = zeit.cms.content.interfaces.ICommonMetadata
    # Sort ICommonMetadata first, so others can override its results
    grok.name('AAA_' + interface.__name__)

    entity_types = {
        # BBB map zeit.intrafind entity_type to retresco.
        'Person': zeit.retresco.interfaces.EntityType('person', 'rtr_persons', 'rtr_persons_main'),
        'Location': zeit.retresco.interfaces.EntityType(
            'location', 'rtr_locations', 'rtr_locations_main'
        ),
        'Organization': zeit.retresco.interfaces.EntityType(
            'organisation', 'rtr_organisations', 'rtr_organisations_main'
        ),
        'free': zeit.retresco.interfaces.EntityType('keyword', 'rtr_keywords', 'rtr_keywords_main'),
    }

    entity_types.update({x.internal: x for x in zeit.retresco.interfaces.ENTITY_TYPES})

    def __call__(self):
        section = None
        if self.context.ressort:
            section = '/' + self.context.ressort
            if self.context.sub_ressort:
                section += '/' + self.context.sub_ressort
        result = {
            'title': self.context.title,
            'teaser': self.context.teaserText or self.context.title,
            # The following (top-level keys) are not strictly required,
            # but are used by TMS UI (for display and filtering).
            'supertitle': self.context.supertitle,
            'section': section,
            'author': ', '.join([x.target.display_name for x in self.context.authorships]),
        }
        for typ in zeit.retresco.interfaces.ENTITY_TYPES:
            result[typ.external] = []
            result[typ.main] = []
        for kw in self.context.keywords:
            entity = self.entity_types.get(kw.entity_type)
            if not entity:
                entity = self.entity_types.get('keyword')
            result[entity.external].append(kw.label)
            if kw.main:
                result[entity.main].append(kw.label)

        result['payload'] = {}
        result['payload']['head'] = {
            'authors': [x.target.uniqueId for x in self.context.authorships],
            'agencies': [x.uniqueId for x in self.context.agencies],
        }
        result['payload']['body'] = {
            'supertitle': self.context.supertitle,
            'title': self.context.title,
            'subtitle': self.context.subtitle,
        }
        result['payload']['teaser'] = {
            'supertitle': self.context.teaserSupertitle,
            'title': self.context.teaserTitle,
            'text': self.context.teaserText,
        }
        return result


class PublishInfo(Converter):
    interface = zeit.cms.workflow.interfaces.IPublishInfo
    grok.name(interface.__name__)

    def __call__(self):
        tms_date = self.context.date_last_published_semantic
        if not tms_date:
            tms_date = self.context.date_first_released
        if not tms_date:
            tms_date = ISemanticChange(self.content).last_semantic_change
        # This field is required by TMS, so always fill with *something*.
        if not tms_date:
            tms_date = MIN_DATE
        return {
            # TMS insists on this precise date format, instead of supporting
            # general ISO8601, sigh.
            'date': tms_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }


class ImageReference(Converter):
    interface = zeit.content.image.interfaces.IImages
    grok.name(interface.__name__)

    def __call__(self):
        image = self.context.image
        if image is None:
            return {}
        return {
            'teaser_img_url': image.uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE, '/'),
            'teaser_img_subline': IImageMetadata(image).caption,
            'payload': {
                'head': {
                    'teaser_image': image.uniqueId,
                    'teaser_image_fill_color': self.context.fill_color,
                }
            },
        }


class SEO(Converter):
    interface = zeit.seo.interfaces.ISEO
    grok.name(interface.__name__)

    def __call__(self):
        if not self.context.meta_robots:
            return {}
        return {'payload': {'seo': {'robots': re.split(', *', self.context.meta_robots)}}}


class Push(Converter):
    """We have to index IPushMessages.message_config explicitly, since the DAV
    property is serialized as xmlpickle, which is not queryable. Additionally,
    we transpose its structure from
    {type: typ1, key1: val1, ...}, {type: typ2, ...}, ...] to
    {
     typ1: {key1: [val1, val2, ...], ...},
     typ2: {key1: [val3, ...], ...},
    }
    to create something that can be queried.
    """

    interface = zeit.push.interfaces.IPushMessages
    grok.name(interface.__name__)

    def __call__(self):
        if not self.context.message_config:
            return {}
        result = {}
        for config in self.context.message_config:
            typ = config.pop('type', None)
            if not typ:
                continue
            config.pop('enabled', None)
            data = result.setdefault(typ, {})
            for key, value in config.items():
                # XXX Work around zope.xmlpickle serialization bug; we *know*
                # that (currently) message_config uses no int anywhere.
                if isinstance(value, int):
                    value = bool(value)
                data.setdefault(key, []).append(value)
        return {'payload': {'push': result}}


class Author(Converter):
    interface = zeit.content.author.interfaces.IAuthor
    grok.name(interface.__name__)

    def __call__(self):
        result = {
            'title': self.context.display_name,
            'teaser': self.context.summary or self.context.display_name,
            'payload': {
                'xml': get_xml_properties(self.context),
                'body': {
                    'supertitle': self.context.summary,
                    'title': self.context.display_name,
                    'text': self.context.biography,
                },
            },
        }
        xml = result['payload']['xml']
        # BBB, remove after WCM-473
        xml['firstname'] = self.context.firstname
        xml['lastname'] = self.context.lastname
        return result


class DynamicFolder(Converter):
    interface = zeit.content.dynamicfolder.interfaces.IDynamicFolder
    grok.name(interface.__name__)

    def __call__(self):
        return {
            # Required fields, so make sure to always index.
            'title': self.content.__name__,
            'teaser': self.content.__name__,
        }


class Gallery(Converter):
    interface = zeit.content.gallery.interfaces.IGallery
    grok.name(interface.__name__)

    def __call__(self):
        return {
            'payload': {
                'head': {
                    'visible_entry_count': (
                        zeit.content.gallery.interfaces.IVisibleEntryCount(self.context)
                    ),
                }
            }
        }


class Image(Converter):
    interface = zeit.content.image.interfaces.IImageMetadata
    grok.name(interface.__name__)

    def __new__(cls, context):
        if '/news/' in context.uniqueId:
            # skip zeit.newsimport images. Unfortunately, image(groups) have no
            # ressort or product-id with which we could filter this.
            return None
        return super().__new__(cls, context)

    def __call__(self):
        title = self.context.title or self.content.__name__
        return {
            # Required fields, so make sure to always index (for zeit.find).
            'title': title,
            'teaser': self.context.caption or title,
            'payload': {
                'body': {
                    'title': title,
                    'text': self.context.caption or title,
                }
            },
        }


class Infobox(Converter):
    interface = zeit.content.infobox.interfaces.IInfobox
    grok.name(interface.__name__)

    def __call__(self):
        result = {
            'title': self.context.supertitle,
            'teaser': self.context.supertitle,
            'payload': {
                'body': {
                    'supertitle': self.context.supertitle,
                }
            },
        }
        if self.context.contents and self.context.contents[0]:
            title, text = self.context.contents[0]
            result['payload']['body'].update(title=title, text=text)
        return result


class Link(Converter):
    interface = zeit.content.link.interfaces.ILink
    grok.name(interface.__name__)

    def __call__(self):
        return {
            'title': self.context.url,
            'teaser': self.context.url,
            'payload': {
                'body': {
                    'url': self.context.url,
                    'target': self.context.target,
                    'nofollow': self.context.nofollow,
                }
            },
        }


class Portraitbox(Converter):
    interface = zeit.content.portraitbox.interfaces.IPortraitbox
    grok.name(interface.__name__)

    def __call__(self):
        return {
            'title': self.context.name,
            'teaser': self.context.text,
            'payload': {
                'body': {
                    'title': self.context.name,
                    'text': self.context.text,
                }
            },
        }


class Article(Converter):
    interface = zeit.content.article.interfaces.IArticle
    grok.name(interface.__name__)

    def __call__(self):
        return {
            'payload': {
                'head': {
                    'audio_references': [x.uniqueId for x in IAudioReferences(self.context).items]
                }
            }
        }


class Recipe(Converter):
    interface = zeit.wochenmarkt.recipe.IRecipeArticle
    grok.name(interface.__name__)

    def __call__(self):
        recipe = self._convert_recipe()
        return {'payload': {'recipe': recipe}} if recipe else {}

    def _convert_recipe(self):
        recipes = list(self.content.body.filter_values(IRecipeList))
        ingredients = list(itertools.chain(*[x.ingredients for x in recipes]))
        if not (self.context.categories or ingredients):
            return None
        search_list = []

        categories = []
        source = zeit.wochenmarkt.sources.recipeCategoriesSource(self.content)
        for category in self.context.categories:
            meta = source.find(category.id)
            if meta and meta.flag == 'no-search':
                continue
            categories.append(category)

        search_list += [f'{x.name}:category' for x in categories]
        source = zeit.wochenmarkt.sources.ingredientsSource(self.content)
        for ingredient in ingredients:
            i = source.find(ingredient.code)
            search_list += [f'{x}:ingredient' for x in i.qwords]

        titles = [x.title for x in recipes if x.title]
        search_list += [f'{x}:recipe_title' for x in titles]
        subheadings = [x.subheading for x in recipes if x.searchable_subheading]
        search_list += [f'{x}:subheading' for x in subheadings]
        search_list.append(f'{self.content.title}:title')

        source = zeit.content.modules.interfaces.RecipeComplexitySource(None).factory
        complexities = [source.getTitle(None, x.complexity) for x in recipes if x.complexity]
        source = zeit.content.modules.interfaces.RecipeTimeSource(None).factory
        times = [source.getTitle(None, x.time) for x in recipes if x.time]

        return {
            'categories': [x.code for x in categories],
            'search': list(set(search_list)),
            'ingredients': list(set([x.code for x in ingredients])),
            'titles': list(set(titles)),
            'subheadings': list(set(subheadings)),
            'complexities': list(set(complexities)),
            'servings': list(set([x.servings for x in recipes])),
            'times': list(set(times)),
        }


class Text(Converter):
    interface = zeit.content.text.interfaces.IText
    grok.name(interface.__name__)

    def __call__(self):
        return {
            'title': self.context.__name__,
            'teaser': self.context.__name__,
            'payload': {
                'body': {
                    'title': self.context.__name__,
                }
            },
        }


class RawXML(Converter):
    interface = zeit.content.rawxml.interfaces.IRawXML
    grok.name(interface.__name__)

    def __call__(self):
        return {
            'title': self.context.title,
            'teaser': self.context.title,
            'payload': {
                'body': {
                    'title': self.context.__name__,
                }
            },
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
        instance = super(zeit.cms.grok.IndirectAdapter, cls).__new__(cls)
        instance.context = context
        instance.content = context
        return instance

    def __call__(self):
        result = {
            'title': self.context.volume_note or 'Ausgabe',
            'teaser': self.context.volume_note or 'Ausgabe',
        }
        covers = [
            {'id': x.get('id'), 'product_id': x.get('product_id'), 'href': x.get('href')}
            for x in self.context.xml.xpath('//covers/cover')
        ]
        if covers:
            result['payload'] = {'head': {'covers': covers}}
        return result


class CMSSearch(Converter):
    # For zeit.find

    interface = zeit.cms.interfaces.ICMSContent
    grok.name('zeit.find')

    DUMMY_REQUEST = zope.publisher.browser.TestRequest(skin=zeit.cms.browser.interfaces.ICMSSkin)
    SERVER_URL = DUMMY_REQUEST['SERVER_URL']

    def __call__(self):
        icon = zope.component.queryMultiAdapter((self.context, self.DUMMY_REQUEST), name='zmi_icon')
        icon_url = icon and icon.url().replace(self.SERVER_URL, '')

        preview = zope.component.queryMultiAdapter(
            (self.context, self.DUMMY_REQUEST), name='thumbnail'
        )
        if preview is not None:
            # XXX Using IAbsoluteURL would have to resolve the __parent__
            # chain, which is way too slow in bulk reindex situations (where
            # we have no DAV cache to avoid conflict errors). So we cheat and
            # duplicate URL structure knowledge instead.
            preview_url = os.path.join(self.context.uniqueId, preview.__name__)
            preview_url = preview_url.replace(zeit.cms.interfaces.ID_NAMESPACE, '/repository/')
        else:
            preview_url = None

        return {
            'payload': {
                'vivi': {
                    'cms_icon': icon_url,
                    'cms_preview_url': preview_url,
                    'publish_status': IPublicationStatus(self.content).published,
                }
            }
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
    return context.xml.find('body')


def get_xml_properties(context):
    cls = type(context)
    result = {}
    for name in dir(cls):
        prop = getattr(cls, name)
        if isinstance(prop, zeit.cms.content.property.ObjectPathProperty):
            value = getattr(context, name)
            if value:
                result[name] = value
    return result


def merge_and_skip_empty(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge_and_skip_empty(value, node)
        elif value is not None and value != '':  # skip empty values
            destination[key] = value
    return destination
