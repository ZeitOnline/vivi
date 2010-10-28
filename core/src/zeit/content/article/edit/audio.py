# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


class Audio(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IAudio)
    type = 'audio'

    audio_id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'audioID',
        zeit.content.article.edit.interfaces.IAudio['audio_id'])
    expires = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty(
            '.', 'expires'),
        zeit.content.article.edit.interfaces.IAudio['expires'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Audio
    title = _('Audio')
