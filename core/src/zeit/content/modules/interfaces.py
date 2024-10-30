import re

import grokcore.component as grok
import zope.app.appsetup.product
import zope.schema

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.content.image.interfaces
import zeit.content.text.interfaces
import zeit.edit.interfaces
import zeit.wochenmarkt.ingredients


class IRawText(zeit.edit.interfaces.IBlock):
    text_reference = zope.schema.Choice(
        title=_('Raw text reference'),
        required=False,
        source=zeit.content.text.interfaces.embedSource,
    )

    text = zope.schema.Text(title=_('Raw text'), required=False)

    raw_code = zope.interface.Attribute('Raw code from text or text_reference')

    params = zope.interface.Attribute('Our IEmbedParameters dict')


class IEmbedParameters(zope.interface.common.mapping.IMapping):
    pass


# XXX Both article and cp use a "raw xml" module, but their XML serialization
# is so different that they don't really share any code.


class EmbedProviderSource(zeit.cms.content.sources.SimpleXMLSource):
    product_configuration = 'zeit.content.modules'
    config_url = 'embed-provider-source'
    default_filename = 'embed-providers.xml'


EMBED_PROVIDER_SOURCE = EmbedProviderSource()


class URIChoice(zope.schema.URI):
    def __init__(self, *args, **kw):
        self.source = kw.pop('source')
        placeholder = kw.pop('placeholder')
        super().__init__(*args, **kw)
        self.setTaggedValue('placeholder', placeholder)

    def _validate(self, value):
        super()._validate(value)
        if self.context.extract_domain(value) not in self.source:
            raise zeit.cms.interfaces.ValidationError(_('Unsupported embed domain'))


class IEmbed(zeit.edit.interfaces.IBlock):
    url = URIChoice(title=_('Embed URL'), placeholder=_('Add URL'), source=EMBED_PROVIDER_SOURCE)

    domain = zope.interface.Attribute('The secondlevel domain of our `url`')

    def extract_domain(url):
        pass


class IJobTicker(zeit.edit.interfaces.IBlock):
    feed = zope.schema.Choice(
        title=_('Jobbox Ticker'), required=True, values=()
    )  # actual source must be set in concrete subclass

    title = zope.interface.Attribute('Title of the chosen feed')


class Newsletter(zeit.cms.content.sources.AllowedBase):
    def __init__(self, id, title, image, abo_text, anon_text, redirect_link, legal_text, kicker):
        super().__init__(id, title, available=None)
        self.image = image
        self.abo_text = abo_text
        self.anon_text = anon_text
        self.redirect_link = redirect_link
        self.legal_text = legal_text
        self.kicker = kicker


@grok.implementer(zeit.content.image.interfaces.IImages)
class NewsletterImage(grok.Adapter):
    grok.context(Newsletter)

    fill_color = None

    @property
    def image(self):
        return zeit.cms.interfaces.ICMSContent(self.context.image, None)


class NewsletterSource(zeit.cms.content.sources.ObjectSource, zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.content.modules'
    config_url = 'newsletter-source'
    default_filename = 'newsletter.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = {}
        tree = self._get_tree()
        for node in tree.iterchildren('*'):
            newsletter = Newsletter(
                node.get('id'),
                self.child(node, 'title'),
                self.child(node, 'image'),
                self.child(node, 'text'),
                self.child(node, 'text_anonymous'),
                self.child(node, 'redirect_link'),
                self.child(node, 'legal_text'),
                self.child(node, 'kicker'),
            )
            result[newsletter.id] = newsletter
        return result

    def child(self, node, name):
        child = node.find(name)
        if child is None:
            return None
        if not child.text:
            return ''
        return child.text.strip()


class INewsletterSignup(zeit.edit.interfaces.IBlock):
    newsletter = zope.schema.Choice(title=_('Newsletter Signup'), source=NewsletterSource())

    prefix_text = zope.schema.Text(
        title=_('Newslettersignup Prefix'), description=_('Use Markdown'), required=False
    )


class IQuiz(zeit.edit.interfaces.IBlock):
    quiz_id = zope.schema.TextLine(title=_('Quiz id'))
    adreload_enabled = zope.schema.Bool(title=_('Enable adreload'), default=True)


def validate_email(string):
    if not string:
        return True
    if '@' not in string:
        raise zeit.cms.interfaces.ValidationError(_('Email address must contain @.'))
    return True


class SubjectSource(zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.content.modules'
    config_url = 'subject-source'
    default_filename = 'mail-subjects.xml'
    attribute = 'id'


SUBJECT_SOURCE = SubjectSource()


class IMail(zeit.edit.interfaces.IBlock):
    title = zope.schema.TextLine(title=_('Title'), required=False)

    subtitle = zope.schema.Text(title=_('Subtitle'), required=False)

    to = zope.schema.TextLine(title=_('Recipient'), constraint=validate_email)

    subject = zope.schema.Choice(title=_('Subject'), source=SUBJECT_SOURCE, required=False)

    subject_display = zope.schema.TextLine(title=_('Subject'), readonly=True)

    success_message = zope.schema.TextLine(title=_('Success message'))

    email_required = zope.schema.Bool(title=_('Email required?'), default=False)

    body = zope.interface.Attribute('Email body')


class RecipeMetadataSource(zeit.cms.content.sources.SearchableXMLSource):
    product_configuration = 'zeit.content.modules'
    config_url = 'recipe-metadata-source'
    default_filename = 'recipe-metadata.xml'

    def getNodes(self):
        tree = self._get_tree()
        return tree.xpath(self.xpath)


class RecipeUnitsSource(RecipeMetadataSource):
    def __init__(self):
        super().__init__('//unit')


# Servings are valid if all of these are satisfied:
# <num> is a number > 0
# format is: <num> or <num>-<num>
VALID_SERVINGS = re.compile(r'^[1-9]\d*(-\d+)?$')


def validate_servings(value):
    if VALID_SERVINGS.match(value) is not None:
        try:
            v = list(map(int, value.split('-')))
            # In case it's a range, the second value must be higher.
            if len(v) == 1 or int(v[0]) < int(v[1]):
                return True
        except ValueError:
            pass
    raise zeit.cms.interfaces.ValidationError(_('Value must be number or range.'))


class IRecipeList(zeit.edit.interfaces.IBlock):
    merge_with_previous = zope.schema.Bool(
        title=_('Merge with previous recipe list module'), default=False
    )

    title = zope.schema.TextLine(title=_('Recipe name'), required=False)

    subheading = zope.schema.TextLine(title=_('Subheading'), required=False)

    searchable_subheading = zope.schema.Bool(title=_('Appears in recipe search?'), default=False)

    complexity = zope.schema.Choice(
        title=_('Complexity'), source=RecipeMetadataSource('*//complexity'), required=False
    )

    time = zope.schema.Choice(
        title=_('Time'), source=RecipeMetadataSource('*//time'), required=False
    )

    servings = zope.schema.TextLine(
        title=_('Servings'), required=False, constraint=validate_servings
    )

    special_ingredient = zope.schema.TextLine(
        title=_('Special ingredient'),
        description=_(
            'A non-searchable free text ingredient without a cp ' '(e.g. an extra portion of love)'
        ),
        required=False,
    )

    ingredients = zope.schema.Tuple(
        title=_('Ingredients'),
        value_type=zope.schema.Choice(source=zeit.wochenmarkt.sources.ingredientsSource),
        default=(),
        required=False,
    )


class LiveblogSource(zeit.cms.content.sources.SearchableXMLSource):
    """A source for all liveblog config."""

    attribute = 'id'
    default_filename = 'liveblog.xml'
    product_configuration = 'zeit.content.modules'


class TimelineTemplateSource(zeit.cms.content.sources.SimpleDictSource):
    values = {
        'highlighted': _('Highlighted events'),
        'recent': _('Recent events'),
        'disabled': _('No timeline in teaser'),
    }


class ITickarooLiveblog(zeit.edit.interfaces.IBlock):
    liveblog_id = zope.schema.TextLine(title=_('Liveblog id'))

    collapse_preceding_content = zope.schema.Bool(
        title=_('Collapse preceding content'), default=True, required=False
    )

    timeline_template = zope.schema.Choice(
        title=_('Timeline Content'),
        default='disabled',
        required=True,
        source=TimelineTemplateSource(),
    )

    status = zope.schema.Choice(
        title=_('Liveblog status'), source=LiveblogSource('*//status'), required=True
    )

    theme = zope.schema.Choice(
        title=_('Liveblog theme'),
        source=LiveblogSource('*//theme'),
        default='default',
        required=True,
    )
