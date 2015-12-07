# coding: utf8
from zeit.cms.i18n import MessageFactory as _
import re
import zc.sourcefactory.source
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.content.image.interfaces
import zope.interface
import zope.schema


class StatusSource(zeit.cms.content.sources.SimpleFixedValueSource):

    values = (u'Print', u'Online', u'Reader')


class InvalidCode(zope.schema.ValidationError):
    __doc__ = _('Code contains invalid characters')


valid_vgwortcode_regex = re.compile(r'^[A-Za-z]+$').match


def valid_vgwortcode(value):
    if not valid_vgwortcode_regex(value):
        raise InvalidCode(value)
    return True


class IAuthor(zope.interface.Interface):
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

    vgwortid = zope.schema.Int(
        title=_('VG-Wort ID'),
        required=False,
        # see messageService.wsdl:cardNumberType
        min=10, max=9999999)
    vgwortcode = zope.schema.TextLine(
        title=_('VG-Wort Code'), required=False,
        constraint=valid_vgwortcode)

    display_name = zope.interface.Attribute(
        'The computed display name. Default is "firstname lastname",'
        ' a user entered value takes precedence.')
    entered_display_name = zope.schema.TextLine(
        title=_('Display name'),
        required=False,
        description=_(u"Default: 'Firstname Lastname'"))

    community_profile = zope.schema.TextLine(
        title=_('Community-Profile URL'), required=False)
    status = zope.schema.Choice(
        title=_(u'Redaktionszugehörigkeit'),
        source=StatusSource())
    external = zope.schema.Bool(
        title=_(u'External?'))

    image_group = zope.schema.Choice(
        title=_('Image group'),
        description=_('Drag an image group here'),
        required=False,
        source=zeit.content.image.interfaces.imageGroupSource)

    biography = zope.schema.Text(
        title=_('Short Biography'), required=False)

    bio_questions = zope.interface.Attribute('Our IBiographyQuestions dict')

    favourite_content = zope.schema.Tuple(
        title=_('Favourite content'),
        default=(),
        max_length=3,
        required=False,
        value_type=zope.schema.Choice(
            source=zeit.cms.related.interfaces.relatableContentSource))

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
    attribute = 'id'


BIOGRAPHY_QUESTIONS = BiographyQuestionSource()


class IAuthorReference(zeit.cms.content.interfaces.IReference):

    location = zope.schema.Choice(
        title=_('Location'),
        source=zeit.cms.tagging.source.locationSource,
        required=False)


class IAuthorBioReference(zeit.cms.content.interfaces.IReference):

    biography = zope.schema.Text(
        title=_('Biography'),
        required=False)
