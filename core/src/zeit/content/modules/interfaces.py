from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE
import collections
import grokcore.component as grok
import six
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.content.image.interfaces
import zeit.content.text.interfaces
import zeit.edit.interfaces
import zeit.wochenmarkt.ingredients
import zope.app.appsetup.product
import zope.schema


class IRawText(zeit.edit.interfaces.IBlock):

    text_reference = zope.schema.Choice(
        title=_('Raw text reference'),
        required=False,
        source=zeit.content.text.interfaces.embedSource)

    text = zope.schema.Text(
        title=_('Raw text'),
        required=False)

    raw_code = zope.interface.Attribute('Raw code from text or text_reference')

    params = zope.interface.Attribute('Our IEmbedParameters dict')


class IEmbedParameters(zope.interface.common.mapping.IMapping):
    pass


# XXX Both article and cp use a "raw xml" module, but their XML serialization
# is so different that they don't really share any code.


class EmbedProviderSource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.content.modules'
    config_url = 'embed-provider-source'


EMBED_PROVIDER_SOURCE = EmbedProviderSource()


class URIChoice(zope.schema.URI):

    def __init__(self, *args, **kw):
        self.source = kw.pop('source')
        placeholder = kw.pop('placeholder')
        super(URIChoice, self).__init__(*args, **kw)
        self.setTaggedValue('placeholder', placeholder)

    def _validate(self, value):
        super(URIChoice, self)._validate(value)
        if self.context.extract_domain(value) not in self.source:
            raise zeit.cms.interfaces.ValidationError(
                _('Unsupported embed domain'))


class IEmbed(zeit.edit.interfaces.IBlock):

    url = URIChoice(title=_('Embed URL'),
                    placeholder=_('Add URL'),
                    source=EMBED_PROVIDER_SOURCE)

    domain = zope.interface.Attribute('The secondlevel domain of our `url`')

    def extract_domain(url):
        pass


class IJobTicker(zeit.edit.interfaces.IBlock):

    feed = zope.schema.Choice(
        title=_('Jobbox Ticker'),
        required=True,
        values=())  # actual source must be set in concrete subclass

    title = zope.interface.Attribute('Title of the chosen feed')


class Newsletter(zeit.cms.content.sources.AllowedBase):

    def __init__(self, id, title, image, abo_text, anon_text):
        super(Newsletter, self).__init__(id, title, available=None)
        self.image = image
        self.abo_text = abo_text
        self.anon_text = anon_text


@grok.implementer(zeit.content.image.interfaces.IImages)
class NewsletterImage(grok.Adapter):

    grok.context(Newsletter)

    fill_color = None

    @property
    def image(self):
        return zeit.cms.interfaces.ICMSContent(self.context.image, None)


class NewsletterSource(zeit.cms.content.sources.ObjectSource,
                       zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.modules'
    config_url = 'newsletter-source'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = collections.OrderedDict()
        tree = self._get_tree()
        for node in tree.iterchildren('*'):
            newsletter = Newsletter(
                six.text_type(node.get('id')),
                self.child(node, 'title'),
                self.child(node, 'image'),
                self.child(node, 'text'),
                self.child(node, 'text_anonymous'),
            )
            result[newsletter.id] = newsletter
        return result

    def child(self, node, name):
        child = node.find(name)
        if child is None:
            return None
        return six.text_type(child.text).strip()


class INewsletterSignup(zeit.edit.interfaces.IBlock):

    newsletter = zope.schema.Choice(
        title=_('Newsletter Signup'),
        source=NewsletterSource())


class IQuiz(zeit.edit.interfaces.IBlock):

    quiz_id = zope.schema.TextLine(
        title=_('Quiz id'))
    adreload_enabled = zope.schema.Bool(
        title=_('Enable adreload'),
        default=True)


def validate_email(string):
    if not string:
        return True
    if '@' not in string:
        raise zeit.cms.interfaces.ValidationError(
            _('Email address must contain @.'))
    return True


class SubjectSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.modules'
    config_url = 'subject-source'
    attribute = 'id'


SUBJECT_SOURCE = SubjectSource()


class IMail(zeit.edit.interfaces.IBlock):

    title = zope.schema.TextLine(
        title=_('Title'),
        required=False)

    subtitle = zope.schema.Text(
        title=_('Subtitle'),
        required=False)

    to = zope.schema.TextLine(
        title=_('Recipient'),
        constraint=validate_email)

    subject = zope.schema.Choice(
        title=_('Subject'),
        source=SUBJECT_SOURCE,
        required=False)

    subject_display = zope.schema.TextLine(
        title=_('Subject'),
        readonly=True)

    success_message = zope.schema.TextLine(
        title=_('Success message'))

    email_required = zope.schema.Bool(
        title=_('Email required?'),
        default=False)

    body = zope.interface.Attribute('Email body')


def validate_servings(value):
    try:
        if int(value) <= 0:
            raise ValueError
    except ValueError:
        raise zeit.cms.interfaces.ValidationError(
            _('Servings must be a positive number or empty.'))
    else:
        return True


class RecipeMetadataSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.modules'
    config_url = 'recipe-metadata-source'

    def __init__(self, xpath):
        super(RecipeMetadataSource, self).__init__()
        self.xpath = xpath

    def getValues(self, context):
        tree = self._get_tree()
        return [six.text_type(node) for node in tree.xpath(self.xpath)]


class IRecipeList(zeit.edit.interfaces.IBlock):

    name = zope.schema.TextLine(
        title=_('Title'),
        required=False)

    searchable_title = zope.schema.Bool(
        title=_('Appears in recipe search?'),
        default=False)

    complexity = zope.schema.Choice(
        title=_("Complexity"),
        source=RecipeMetadataSource("*//complexity"),
        required=True)

    time = zope.schema.Choice(
        title=_("Time"),
        source=RecipeMetadataSource("*//time"),
        required=True)

    servings = zope.schema.TextLine(
        title=_('Servings'),
        required=False,
        constraint=validate_servings)

    ingredients = zope.schema.Tuple(
        title=_("Ingredients"),
        value_type=zope.schema.Choice(
            source=zeit.wochenmarkt.ingredients.ingredientsSource),
        default=(),
        required=False)
