from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import IAdplace
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


class Adplace(zeit.content.article.edit.block.Block):

    grok.implements(IAdplace)
    type = 'adplace'

    tile = ObjectPathAttributeProperty(
        '.', 'tile', IAdplace['tile'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Adplace
    title = _('Adplace block')
