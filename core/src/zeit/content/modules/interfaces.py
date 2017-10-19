from zeit.cms.i18n import MessageFactory as _
import zeit.content.text.interfaces
import zeit.edit.interfaces
import zope.schema


class IRawText(zeit.edit.interfaces.IBlock):

    text_reference = zope.schema.Choice(
        title=_('Raw text reference'),
        required=False,
        source=zeit.content.text.interfaces.textSource)

    text = zope.schema.Text(
        title=_('Raw text'),
        required=False)

    raw_code = zope.interface.Attribute('Raw code from text or text_reference')


# XXX Both article and cp use a "raw xml" module, but their XML serialization
# is so different that they don't really share any code.
