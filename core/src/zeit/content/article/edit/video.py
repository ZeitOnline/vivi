# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.lxml.interfaces
import grokcore.component
import lxml.objectify
import zeit.brightcove.asset
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component
import zope.schema


class Video(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IVideo)
    type = 'video'

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'format', zope.schema.TextLine())

    @property
    def video(self):
        return zeit.cms.interfaces.ICMSContent(self.xml.get('href'), None)

    @video.setter
    def video(self, value):
        self._set_video('href', value)

    @property
    def video_2(self):
        return zeit.cms.interfaces.ICMSContent(self.xml.get('href2'), None)

    @video_2.setter
    def video_2(self, value):
        self._set_video('href2', value)

    def _set_video(self, attribute, video):
        if video is None:
            self.xml.attrib.pop(attribute, None)
        else:
            self.xml.set(attribute, video.uniqueId)
        self.xml.set(
            'expires', zeit.brightcove.asset.get_expires(self.video,
                                                         self.video_2))



class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Video
    title = _('Video')


@grokcore.component.adapter(zeit.content.article.edit.interfaces.IEditableBody,
                            zeit.brightcove.interfaces.IBrightcoveContent)
@grokcore.component.implementer(zeit.edit.interfaces.IElement)
def factor_image_block_from_image(body, context):
    block = Factory(body)()
    block.video = context
    return block
