# coding: utf8
from zeit.cms.i18n import MessageFactory as _
import re
import zc.sourcefactory.source
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.related.interfaces
import zeit.content.image.interfaces
import zope.interface
import zeit.retresco.interfaces
import zope.schema


class StatusSource(zeit.cms.content.sources.SimpleFixedValueSource):

    values = ('Print', 'Online', 'Reader', 'Agentur')


class InvalidCode(zope.schema.ValidationError):
    __doc__ = _('Code contains invalid characters')


valid_vgwortcode_regex = re.compile(r'^[A-Za-z]+$').match


def valid_vgwortcode(value):
    if not valid_vgwortcode_regex(value):
        raise InvalidCode(value)
    return True


class IAuthor(zope.interface.Interface,
              zeit.retresco.interfaces.ISkipEnrich):
    """An author writes CMS content."""

    title = zope.schema.TextLine(title=_('Title'), required=False)
    firstname = zope.schema.TextLine(title=_('Firstname'))
    lastname = zope.schema.TextLine(title=_('Lastname'))
    summary = zope.schema.TextLine(
        title=_('Summary'), required=False,
        description=_('Author summary description'))

    email = zope.schema.TextLine(title=_('Email address'), required=False)
    twitter = zope.schema.TextLine(title=_('Twitter handle'), required=False)
    facebook = zope.schema.TextLine(title=_('Facebook handle'), required=False)
    instagram = zope.schema.TextLine(
        title=_('Instagram handle'), required=False)
    jabber = zope.schema.TextLine(title=_('Jabber handle'), required=False)
    signal = zope.schema.TextLine(title=_('Signal handle'), required=False)
    threema = zope.schema.TextLine(title=_('Threema id'), required=False)
    additional_contact_title = zope.schema.TextLine(title=_(
        'additional contact title'), required=False)
    additional_contact_content = zope.schema.TextLine(title=_(
        'additional contact content'), required=False)
    pgp = zope.schema.TextLine(title=_('PGP key'), required=False)
    website = zope.schema.TextLine(title=_('Website handle'), required=False)

    vgwortid = zope.schema.Int(
        title=_('VG-Wort ID'),
        required=False,
        # see messageService.wsdl:cardNumberType
        min=10, max=9999999)

    vgwortcode = zope.schema.TextLine(
        title=_('VG-Wort Code'), required=False,
        constraint=valid_vgwortcode)

    honorar_id = zope.schema.TextLine(
        title=_('Honorar ID'), required=False)

    display_name = zope.schema.TextLine(
        title='The computed display name. Default is "firstname lastname",'
              ' a user entered value takes precedence.',
        required=False)

    entered_display_name = zope.schema.TextLine(
        title=_('Display name'),
        required=False,
        description=_("Default: 'Firstname Lastname'"))

    initials = zope.schema.TextLine(
        title=_('Initials'), required=False)

    community_profile = zope.schema.TextLine(
        title=_('Community-Profile URL'), required=False)

    ssoid = zope.schema.Int(
        title=_('SSO-Id'), required=False, min=10, max=9999999)

    sso_connect = zope.schema.Bool(
        title=_('Connect with SSO-Account'),
        default=True)

    status = zope.schema.Choice(
        title=_('Redaktionszugehörigkeit'),
        source=StatusSource(),
        required=False)

    external = zope.schema.Bool(
        title=_('External?'))

    is_author = zope.schema.Bool(
        title=_('is author'),
        default=True)

    is_cook = zope.schema.Bool(
        title=_('is cook'))

    enable_followpush = zope.schema.Bool(
        title=_('Enable followpush?'))

    enable_feedback = zope.schema.Bool(
        title=_('Enable feedback?'), default=False)

    show_letterbox_link = zope.schema.Bool(
        title=_('Link letterbox'), default=False)

    biography = zope.schema.Text(
        title=_('Short Biography'), required=False)

    cook_biography = zope.schema.Text(
        title=_('Short Cook Biography'), required=False)

    bio_questions = zope.interface.Attribute('Our IBiographyQuestions dict')

    favourite_content = zope.schema.Tuple(
        title=_('Favourite content'),
        default=(),
        max_length=3,
        required=False,
        value_type=zope.schema.Choice(
            source=zeit.cms.related.interfaces.relatableContentSource))

    occupation = zope.schema.TextLine(
        title=_('Occupation'),
        max_length=16,
        required=False
    )

    topiclink_label_1 = zope.schema.TextLine(
        title=_('Label for favourite topic #1'),
        required=False)

    topiclink_label_2 = zope.schema.TextLine(
        title=_('Label for favourite topic #2'),
        required=False)

    topiclink_label_3 = zope.schema.TextLine(
        title=_('Label for favourite topic #3'),
        required=False)

    topiclink_url_1 = zope.schema.TextLine(
        title=_('URL for favourite topic #1'),
        required=False)

    topiclink_url_2 = zope.schema.TextLine(
        title=_('URL for favourite topic #2'),
        required=False)

    topiclink_url_3 = zope.schema.TextLine(
        title=_('URL for favourite topic #3'),
        required=False)


class IBiographyQuestions(zope.interface.common.mapping.IMapping):
    """dict that maps a question id -> IQuestion

    Contains values for all question ids configured via BIOGRAPHY_QUESTIONS,
    their ``.answer`` is None when the author has no data for that question id.
    """


class IQuestion(zope.interface.Interface):

    id = zope.schema.TextLine(readonly=True)
    title = zope.schema.TextLine(readonly=True)
    answer = zope.schema.TextLine(readonly=True)


class BiographyQuestionSource(zeit.cms.content.sources.XMLSource):

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def title(self, id):
            return self.factory.getTitle(self.context, id)

    product_configuration = 'zeit.content.author'
    config_url = 'biography-questions'
    default_filename = 'author-biography-questions.xml'
    attribute = 'id'


BIOGRAPHY_QUESTIONS = BiographyQuestionSource()


class RoleSource(zeit.cms.content.sources.SimpleContextualXMLSource):

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def report_to_vgwort(self, value):
            if not value:
                return True
            nodes = self.factory._get_tree().xpath('//*[text()="%s"]' % value)
            if not nodes:
                return False
            return nodes[0].get('vgwort') == 'true'

    product_configuration = 'zeit.content.author'
    config_url = 'roles'
    default_filename = 'author-roles.xml'


ROLE_SOURCE = RoleSource()


class IAuthorReference(zeit.cms.content.interfaces.IReference):

    location = zope.schema.Choice(
        title=_('Location'),
        source=zeit.cms.tagging.source.locationSource,
        required=False)

    role = zope.schema.Choice(
        title=_('Author role'),
        source=ROLE_SOURCE,
        required=False)


class IAuthorBioReference(zeit.cms.content.interfaces.IReference):

    biography = zope.schema.Text(
        title=_('Biography'),
        required=False)


class IHonorar(zope.interface.Interface):
    """Connection to the honorar system (HDok)."""

    def search(substring):
        pass

    def create(data):
        pass

    def invalid_gcids(timestamp):
        pass
