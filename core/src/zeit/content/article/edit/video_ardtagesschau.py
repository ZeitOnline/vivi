import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok


@grok.implementer(zeit.content.article.edit.interfaces.IVideoARDTagesschau)
class VideoARDTagesschau(zeit.content.article.edit.block.Block):

    type = 'video_ardtagesschau'

    video_ardtagesschau_data = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'text', zeit.content.article.edit.interfaces.IVideoARDTagesschau[
        'video_ardtagesschau_data'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = VideoARDTagesschau
    title = _('Video ARD Tagesschau')
