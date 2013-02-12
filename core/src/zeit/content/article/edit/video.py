# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import zeit.content.video.asset
import zeit.content.video.interfaces
import zeit.cms.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.schema


class Video(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IVideo)
    type = 'video'

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        # refers to zeit.content.article.edit.interfaces.IVideo['layout'],
        # but we can't use that here, since legacy data might have all
        # sorts of values for layout, so the field's source would be
        # too restrictive.
        '.', 'format', zope.schema.TextLine(required=False))

    badge = 'video'

    is_empty = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'is_empty',
        zeit.content.article.edit.interfaces.IReference['is_empty'])

    @property
    def video(self):
        return zeit.cms.interfaces.ICMSContent(self.xml.get('href'), None)

    @video.setter
    def video(self, value):
        self._validate('video', value)
        self._set_video('href', value)

    @property
    def video_2(self):
        return zeit.cms.interfaces.ICMSContent(self.xml.get('href2'), None)

    @video_2.setter
    def video_2(self, value):
        self._validate('video_2', value)
        self._set_video('href2', value)

    def _set_video(self, attribute, video):
        if video is None:
            self.xml.attrib.pop(attribute, None)
            self.is_empty = True
        else:
            self.xml.set(attribute, video.uniqueId)
            self.is_empty = False
        self.xml.set(
            'expires', zeit.content.video.asset.get_expires(self.video,
                                                            self.video_2))

    def _validate(self, field_name, value):
        zeit.content.article.edit.interfaces.IVideo[field_name].bind(
            self).validate(value)


class Factory(zeit.content.article.edit.reference.ReferenceFactory):

    produces = Video
    title = _('Video')


@grokcore.component.adapter(zeit.content.article.edit.interfaces.IEditableBody,
                            zeit.content.video.interfaces.IVideoContent)
@grokcore.component.implementer(zeit.edit.interfaces.IElement)
def create_video_block_from_video(body, context):
    block = Factory(body)()
    block.video = context
    return block


@grokcore.component.subscribe(
    zeit.content.article.edit.interfaces.IVideo,
    zope.lifecycleevent.IObjectModifiedEvent)
def update_empty(context, event):
    context.is_empty = context.video is None and context.video_2 is None


@grokcore.component.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_video_metadata(article, event):
    body = zeit.content.article.edit.interfaces.IEditableBody(article)
    for block in body.values():
        video = zeit.content.article.edit.interfaces.IVideo(block, None)
        if video is not None:
            # Re-assigning the old value updates xml metadata
            video.video = video.video
            video.video_2 = video.video_2
