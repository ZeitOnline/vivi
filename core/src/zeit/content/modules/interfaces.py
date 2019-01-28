from zeit.cms.i18n import MessageFactory as _
import zeit.content.text.interfaces
import zeit.edit.interfaces
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


# XXX Both article and cp use a "raw xml" module, but their XML serialization
# is so different that they don't really share any code.


class IJobTicker(zeit.edit.interfaces.IBlock):

    feed = zope.schema.Choice(
        title=_('Jobbox Ticker'),
        required=True,
        values=())  # actual source must be set in concrete subclass

    title = zope.interface.Attribute('Title of the chosen feed')


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
