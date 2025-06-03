from io import StringIO
import hashlib
import json
import re

import gocept.cache.property
import grokcore.component as grok
import zope.component
import zope.index.text.interfaces
import zope.interface
import zope.security.proxy

from zeit.cms.content.cache import writeabledict
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR, CAN_RETRACT_ERROR
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.cms.type
import zeit.cms.workflow.dependency
import zeit.cms.workflow.interfaces
import zeit.connector.filesystem
import zeit.connector.interfaces
import zeit.content.article.edit.audio
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.audio.interfaces
import zeit.content.modules
import zeit.content.modules.interfaces
import zeit.edit.interfaces
import zeit.edit.rule
import zeit.wochenmarkt.categories
import zeit.workflow.interfaces
import zeit.workflow.workflow


ARTICLE_NS = zeit.content.article.interfaces.ARTICLE_NS
# supertitle+title+subtitle are here since their order is important for XSLT,
# and the XML-properties will reuse existing nodes, so the order will be as we
# want it.
ARTICLE_TEMPLATE = """\
<article>
    <head>
        <header/>
    </head>
    <body>
        <supertitle/>
        <title/>
        <subtitle/>
    </body>
</article>"""


@zope.interface.implementer(
    zeit.content.article.interfaces.IArticle, zeit.cms.interfaces.IEditorialContent
)
class Article(zeit.cms.content.metadata.CommonMetadata):
    """Article is the main content type in the Zeit CMS."""

    default_template = ARTICLE_TEMPLATE

    cache = gocept.cache.property.TransactionBoundCache('_v_article_cache', writeabledict)

    textLength = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['textLength'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'text-length',
    )

    zeit.cms.content.dav.mapProperties(
        zeit.content.article.interfaces.IArticle,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        (
            'has_recensions',
            'artbox_thema',
            'audio_speechbert',
            'genre',
            'template',
            'header_layout',
            'header_color',
            'hide_ligatus_recommendations',
            'prevent_ligatus_indexing',
            'comments_sorting',
            'avoid_create_summary',
        ),
    )

    has_audio = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['has_audio'],
        zeit.cms.interfaces.PRINT_NAMESPACE,
        'has_audio',
        use_default=True,
    )

    @property
    def body(self):
        return zeit.content.article.edit.interfaces.IEditableBody(self)

    @property
    def header(self):
        return zeit.content.article.edit.interfaces.IHeaderArea(self)

    @property
    def paragraphs(self):
        return len(self.xml.xpath('//body/division/p'))

    def updateDAVFromXML(self):
        properties = zeit.connector.interfaces.IWebDAVProperties(self)
        modified = []
        for (name, ns), value in zeit.connector.filesystem.parse_properties(self.xml).items():
            if not value:
                continue
            properties[(name, ns)] = value
            prop = zeit.cms.content.dav.findProperty(
                zeit.cms.content.metadata.CommonMetadata, name, ns
            )
            if prop:
                modified.append(prop.field.__name__)
        zope.lifecycleevent.modified(
            self,
            zope.lifecycleevent.Attributes(zeit.cms.content.interfaces.ICommonMetadata, *modified),
        )

    @property
    def recipe_categories(self):
        if FEATURE_TOGGLES.find('xmlproperty_read_wcm_837'):
            return self._recipe_categories
        else:
            return self._recipe_categories_body

    @recipe_categories.setter
    def recipe_categories(self, value):
        value = list(dict.fromkeys(value))  # ordered set()
        self._recipe_categories = value
        if not FEATURE_TOGGLES.find('xmlproperty_strict_wcm_837'):
            self._recipe_categories_body = value

    @property
    def recipe_ingredients(self):
        return self._recipe_ingredients

    @recipe_ingredients.setter
    def recipe_ingredients(self, value):
        self._recipe_ingredients = sorted(value)

    _recipe_categories = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['recipe_categories'],
        'http://namespaces.zeit.de/CMS/recipe',
        'categories',
        use_default=True,
    )
    _recipe_ingredients = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['recipe_ingredients'],
        zeit.cms.interfaces.RECIPE_SCHEMA_NS,
        'ingredients',
        use_default=True,
    )
    recipe_titles = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['recipe_titles'],
        zeit.cms.interfaces.RECIPE_SCHEMA_NS,
        'titles',
        use_default=True,
    )

    _recipe_categories_body = zeit.wochenmarkt.categories.RecipeCategories()

    @property
    def main_image_block(self):
        try:
            image_block = self.body.values()[0]
        except IndexError:
            return None
        if not zeit.content.article.edit.interfaces.IImage.providedBy(image_block):
            return None
        return image_block

    @property
    def main_image(self):
        image_block = self.main_image_block
        if image_block is None:
            # XXX Duplicates configuration from .edit.image.Image.
            # XXX Kludgy: We're passing the article as the source here, but
            # that will be replaced by having the article create the image
            # block and then use *that* as the source, so it all works out.
            return NoMainImageBlockReference(self, 'references', 'image')
        return image_block.references

    @main_image.setter
    def main_image(self, value):
        image_block = self.main_image_block
        if image_block is None:
            image_block = self._create_image_block_in_front()
        image_block.references = value

    @property
    def main_image_variant_name(self):
        image_block = self.main_image_block
        if image_block is None:
            return None
        return image_block.variant_name

    @main_image_variant_name.setter
    def main_image_variant_name(self, value):
        image_block = self.main_image_block
        if image_block is None:
            return
        image_block.variant_name = value

    def _create_image_block_in_front(self):
        body = self.body
        image_block = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, 'image'
        )()
        ids = body.keys()
        ids.insert(0, ids.pop())  # XXX ElementFactory should do this
        body.updateOrder(ids)
        return image_block

    def get_body(self):
        body = []
        elements = self.body.xml.xpath('(//division/* | //division/ul/*)')
        for elem in elements:
            if elem.tag not in ('intertitle', 'li', 'p'):
                continue
            text = elem.xpath('.//text()')
            if not text:
                continue
            body.append({'content': ' '.join([x.strip() for x in text]), 'type': elem.tag})
        return body


class NoMainImageBlockReference(zeit.cms.content.reference.EmptyReference):
    """We need someone who can create references, even when the reference is
    empty. In case of the main image, not only can the reference be empty,
    the block containing the reference might not even exist. So we need a
    proxy who creates the block if necessary.

    XXX The whole main_image thing is a kludge, and it shows here.
    """

    def create(self, target):
        self.source = self.source._create_image_block_in_front()
        return super().create(target)


class ArticleType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Article
    interface = zeit.content.article.interfaces.IArticle
    type = 'article'
    title = _('Article')


@zope.interface.implementer(zeit.content.article.interfaces.IArticle)
@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
def articleFromTemplate(context):
    source = StringIO(zeit.cms.content.interfaces.IXMLSource(context))
    article = Article(xml_source=source)
    zeit.cms.interfaces.IWebDAVWriteProperties(article).update(
        zeit.cms.interfaces.IWebDAVReadProperties(context)
    )
    return article


@zope.component.adapter(
    zeit.content.article.interfaces.IArticle, zope.lifecycleevent.IObjectModifiedEvent
)
def updateTextLengthOnChange(context, event):
    length = context.xml.find('body').xpath('string-length()')
    try:
        context.textLength = int(length)
    except zope.security.interfaces.Unauthorized:
        # Ignore when we're not allowed to set it.
        pass


@zope.component.adapter(
    zeit.content.article.interfaces.IArticle, zope.lifecycleevent.IObjectModifiedEvent
)
def disallowCommentsIfCommentsAreNotShown(object, event):
    if not zeit.cms.checkout.interfaces.ILocalContent.providedBy(object):
        return
    if not object.commentSectionEnable:
        object.commentsAllowed = False


@grok.subscribe(zeit.content.article.interfaces.IArticle, zope.lifecycleevent.IObjectModifiedEvent)
def modify_speechbert_audio_depeding_on_genre(article, event):
    """Checkbox speechbert audio depends on article-genres.xml"""
    genres = zeit.content.article.interfaces.IArticle['genre'].source(None)
    for desc in event.descriptions:
        if (
            desc.interface is zeit.content.article.interfaces.IArticle
            and 'genre' in desc.attributes
        ):
            if genres.audio(article.genre) == 'speechbert' or not article.genre:
                article.audio_speechbert = True
            else:
                article.audio_speechbert = False


@grok.adapter(zeit.content.article.interfaces.IArticle)
@grok.implementer(zeit.edit.interfaces.IElementReferences)
def iter_referenced_content(context):
    referenced_content = []
    body = context.body
    if not body:
        return referenced_content
    for element in body.values():
        if (
            zeit.content.article.edit.interfaces.IReference.providedBy(element)
            and element.references
        ):
            if zeit.cms.content.interfaces.IReference.providedBy(element.references):
                if element.references.target:
                    referenced_content.append(element.references.target)
            else:
                referenced_content.append(element.references)
    return referenced_content


@grok.implementer(zope.index.text.interfaces.ISearchableText)
class SearchableText(grok.Adapter):
    """SearchableText for an article."""

    grok.context(zeit.content.article.interfaces.IArticle)

    def getSearchableText(self):
        main_text = []
        for p in self.context.xml.xpath('body//p//text()'):
            text = str(p).strip()
            if text:
                main_text.append(text)
        return main_text


@zope.component.adapter(zeit.content.article.interfaces.IArticle)
class ArticleWorkflow(zeit.workflow.workflow.ContentWorkflow):
    def can_publish(self):
        result = super().can_publish()
        if result == CAN_PUBLISH_ERROR:
            return CAN_PUBLISH_ERROR
        validator = zeit.edit.rule.ValidatingWorkflow(self.context)
        result = validator.can_publish()
        self.error_messages = validator.error_messages
        return result

    def can_retract(self):
        result = super().can_retract()
        if result == CAN_RETRACT_ERROR:
            return CAN_RETRACT_ERROR
        validator = zeit.edit.rule.ValidatingWorkflow(self.context)
        result = validator.can_retract()
        self.error_messages = validator.error_messages
        return result


@grok.adapter(zeit.content.article.interfaces.IArticle)
@grok.implementer(zeit.cms.workflow.interfaces.IPublishPriority)
def publish_priority_article(context):
    # Since breaking news should be published faster articles, we give them
    # the same priority as the homepage
    if zeit.content.article.interfaces.IBreakingNews(context).is_breaking:
        return zeit.cms.workflow.interfaces.PRIORITY_HOMEPAGE
    return zeit.cms.workflow.interfaces.PRIORITY_HIGH


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.checkout.interfaces.IBeforeCheckinEvent
)
def ensure_division_handler(context, event):
    context.body.ensure_division()


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.checkout.interfaces.IAfterCheckoutEvent
)
def set_default_values(context, event):
    zeit.cms.content.field.apply_default_values(context, zeit.content.article.interfaces.IArticle)


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.checkout.interfaces.IAfterCheckoutEvent
)
def set_template_and_header_defaults(context, event):
    source = zeit.content.article.source.ARTICLE_TEMPLATE_SOURCE(context)

    if (not context.template and not context.header_layout) or context.template not in source:
        template, header_layout = source.factory.get_default_template(context)

        context.template = template if template else None
        context.header_layout = header_layout if header_layout else None

    source = zeit.content.article.source.MAIN_IMAGE_VARIANT_NAME_SOURCE
    if (
        context.main_image_block
        and context.main_image_block._variant_name not in source(context)
        and (context.template or context.header_layout)
    ):
        context.main_image_variant_name = source.factory.get_default(context)


@grok.subscribe(zeit.content.article.interfaces.IArticle, zope.lifecycleevent.IObjectModifiedEvent)
def set_default_header_when_template_is_changed(context, event):
    for desc in event.descriptions:
        if (
            desc.interface is zeit.content.article.interfaces.IArticle
            and 'template' in desc.attributes
        ):
            break
    else:
        return

    source = zeit.content.article.source.ARTICLE_TEMPLATE_SOURCE(context)
    header_layout = source.factory.get_default_header(context)
    context.header_layout = header_layout if header_layout else None


@grok.subscribe(zeit.content.article.interfaces.IArticle, zope.lifecycleevent.IObjectModifiedEvent)
def set_podcast_header_when_article_has_podcast_audio(context, event):
    for desc in event.descriptions:
        if (
            desc.interface is zeit.content.audio.interfaces.IAudioReferences
            and 'items' in desc.attributes
        ):
            break
    else:
        return

    audio = zeit.content.audio.interfaces.IAudioReferences(context)
    if not audio.items:
        return

    context.header_layout = 'podcast'

    main_audio = audio.items[0]
    if main_audio.audio_type != 'podcast':
        return

    if not context.title:
        context.title = main_audio.title
    episode = zeit.content.audio.interfaces.IPodcastEpisodeInfo(main_audio)
    if not context.teaserText:
        context.teaserText = episode.summary
    if not context.teaserTitle:
        context.teaserTitle = main_audio.title
    if not context.subtitle:
        context.subtitle = episode.summary
    if not context.serie and episode.podcast:
        context.serie = (
            ICommonMetadata['serie'].source(None).find_by_property('url', episode.podcast.id)
        )
    body = context.body
    # article image reserves first position
    if not body or (len(body.keys()) == 1 and context.main_image_block):
        zeit.content.article.edit.audio.apply_notes(body, episode)


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.checkout.interfaces.IAfterCheckoutEvent
)
def ensure_block_ids(context, event):
    body = context.body
    # Keys are generated on demand, so we force this once, otherwise a
    # consistent result is not guaranteed (since different requests might
    # overlap and thus generate different keys).
    body.keys()
    body.ensure_division()


_QUOTE_CHARACTERS = r'[\u201c\u201d\u201e\u201f\u00ab\u00bb]'
QUOTE_CHARACTERS = re.compile(_QUOTE_CHARACTERS)
QUOTE_CHARACTERS_OPEN = re.compile(rf'{_QUOTE_CHARACTERS}(\w)')
QUOTE_CHARACTERS_CLOSE = re.compile(rf'([\w\.]){_QUOTE_CHARACTERS}')


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.checkout.interfaces.IAfterCheckoutEvent
)
def normalize_quotation_marks(context, event):
    normalize = (
        normalize_quotes
        if FEATURE_TOGGLES.find('normalize_quotes')
        else normalize_quotes_to_inch_sign
    )
    normalize(context.xml.find('body'))

    teaser = context.xml.find('teaser')
    if teaser is not None:
        normalize(teaser)


def normalize_quotes(node):
    if node.text:
        node.text = QUOTE_CHARACTERS_OPEN.sub(r'»\1', node.text)
        node.text = QUOTE_CHARACTERS_CLOSE.sub(r'\1«', node.text)
    if node.tail:
        node.tail = QUOTE_CHARACTERS_OPEN.sub(r'»\1', node.tail)
        node.tail = QUOTE_CHARACTERS_CLOSE.sub(r'\1«', node.tail)
    for child in node.iterchildren():
        normalize_quotes(child)


def normalize_quotes_to_inch_sign(node):
    if node.text:
        node.text = QUOTE_CHARACTERS.sub('"', node.text)
    if node.tail:
        node.tail = QUOTE_CHARACTERS.sub('"', node.tail)
    for child in node.iterchildren():
        normalize_quotes_to_inch_sign(child)


@zope.interface.implementer(zeit.content.article.interfaces.ISpeechbertChecksum)
class Speechbert(zeit.cms.content.dav.DAVPropertiesAdapter):
    checksum = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.ISpeechbertChecksum['checksum'],
        zeit.cms.interfaces.SPEECHBERT_NAMESPACE,
        'checksum',
        writeable=zeit.cms.content.interfaces.WRITEABLE_LIVE,
    )

    def _validate(self, checksum: str) -> bool:
        if not self.checksum or not checksum:
            return True
        return self.checksum == checksum

    def calculate(self) -> str:
        speechbert = zope.component.getAdapter(
            self.context, zeit.workflow.interfaces.IPublisherData, name='speechbert'
        )
        if speechbert.ignore('publish'):
            return
        checksum = hashlib.md5(usedforsecurity=False)
        body = json.dumps(self.context.get_body(), ensure_ascii=False).encode('utf-8')
        checksum.update(body)
        return checksum.hexdigest()

    def __eq__(self, other):
        if isinstance(other, str):
            return self._validate(other)
        elif isinstance(other, zeit.content.article.interfaces.ISpeechbertChecksum):
            return self._validate(other.checksum)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.checksum


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.workflow.interfaces.IBeforePublishEvent
)
def calculate_and_set_checksum(context, event):
    article = zeit.content.article.interfaces.ISpeechbertChecksum(context)
    article.checksum = article.calculate()


class AudioDependency(zeit.cms.workflow.dependency.DependencyBase):
    """Articles should always work with published Audio

    Spoiler: Podcasts publishing is dependend on the
    podcasts provider. Therefore we cannot publish with
    the article, but we get the error message and prevent
    the article from being published.
    """

    grok.context(zeit.content.article.interfaces.IArticle)
    grok.name('zeit.content.article')

    retract_dependencies = False

    def get_dependencies(self):
        audio_refs = zeit.content.audio.interfaces.IAudioReferences(self.context, None)
        if audio_refs:
            return audio_refs.items
        return ()


def _categorize_by_ingredients_diet(ingredients):
    source = zeit.wochenmarkt.sources.ingredientsSource(None)
    diets = {source.find(i).diet for i in ingredients}
    categories_source = zeit.wochenmarkt.sources.recipeCategoriesSource(None)
    return categories_source.factory.for_diets(diets)


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.checkout.interfaces.IBeforeCheckinEvent
)
def update_recipes_of_article(context, event):
    if not FEATURE_TOGGLES.find('wcm_19_store_recipes_in_storage'):
        return
    if context.genre not in zeit.wochenmarkt.sources.recipeCategoriesSource.factory.genres:
        return
    recipes = context.body.filter_values(zeit.content.modules.interfaces.IRecipeList)
    titles = [context.title]
    ingredients = set()

    categories = {
        category for category in context.recipe_categories if category.flag != 'no-search'
    }
    categories_source = zeit.wochenmarkt.sources.recipeCategoriesSource
    for recipe in recipes:
        titles.append(recipe.title)
        ingredients = ingredients | {x.id for x in recipe.ingredients}

        if recipe.complexity:
            complexity = categories_source.factory.search(recipe.complexity, flag=None)
            if complexity:
                categories.add(complexity[0])
        if recipe.time:
            time = categories_source.factory.search(recipe.time, flag=None)
            if time:
                categories.add(time[0])
    if category := _categorize_by_ingredients_diet(ingredients):
        categories.add(category)

    context.recipe_titles = titles
    context.recipe_ingredients = ingredients
    context.recipe_categories = categories
