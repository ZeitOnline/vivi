import grokcore.component as grok

from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import IAdplace
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(IAdplace)
class Adplace(zeit.content.article.edit.block.Block):
    type = 'adplace'

    tile = ObjectPathAttributeProperty('.', 'tile', IAdplace['tile'])


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = Adplace
    title = _('Adplace block')
