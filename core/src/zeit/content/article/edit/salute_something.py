from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.ISaluteSomething)
class SaluteSomething(zeit.content.article.edit.block.Block):

    type = 'salute_something'
    import pdb; pdb.set_trace()

    salutation_wording = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'text', zeit.content.article.edit.interfaces.ISaluteSomething[
        'salutation_wording'])
    salutation_object = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'text', zeit.content.article.edit.interfaces.ISaluteSomething[
        'salutation_object'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = SaluteSomething
    title = _('Salute Something')
