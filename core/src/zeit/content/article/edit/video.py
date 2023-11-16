from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.video.interfaces
import zeit.cms.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.reference
import zeit.edit.interfaces
import zope.schema


@grok.implementer(zeit.content.article.edit.interfaces.IVideo)
class Video(zeit.content.article.edit.block.Block):
    type = 'video'

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        # refers to zeit.content.article.edit.interfaces.IVideo['layout'],
        # but we can't use that here, since legacy data might have all
        # sorts of values for layout, so the field's source would be
        # too restrictive.
        '.',
        'format',
        zope.schema.TextLine(required=False),
    )

    badge = 'video'

    is_empty = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'is_empty', zeit.content.article.edit.interfaces.IReference['is_empty']
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        if self.layout is None:
            self.layout = zeit.content.article.edit.interfaces.IVideo['layout'].default

    @property
    def video(self):
        return zeit.cms.interfaces.ICMSContent(self.xml.get('href'), None)

    @video.setter
    def video(self, value):
        self._validate('video', value)
        self._set_video('href', value)

    def _set_video(self, attribute, video):
        if video is None:
            self.xml.attrib.pop(attribute, None)
            self.is_empty = True
        else:
            self.xml.set(attribute, video.uniqueId)
            self.is_empty = False
        expires = getattr(self.video, 'expires', None)
        if expires:
            self.xml.set('expires', expires.isoformat())
        else:
            self.xml.attrib.pop('expires', None)

    def _validate(self, field_name, value):
        zeit.content.article.edit.interfaces.IVideo[field_name].bind(self).validate(value)


class Factory(zeit.content.article.edit.reference.ReferenceFactory):
    produces = Video
    title = _('Video')


@grok.adapter(
    zeit.content.article.edit.interfaces.IArticleArea,
    zeit.content.video.interfaces.IVideoContent,
    int,
)
@grok.implementer(zeit.edit.interfaces.IElement)
def create_video_block_from_video(body, context, position):
    block = Factory(body)(position)
    block.video = context
    return block


@grok.subscribe(
    zeit.content.article.edit.interfaces.IVideo, zope.lifecycleevent.IObjectModifiedEvent
)
def update_empty(context, event):
    context.is_empty = context.video is None


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.checkout.interfaces.IBeforeCheckinEvent
)
def update_video_metadata(article, event):
    for block in article.body.values():
        video = zeit.content.article.edit.interfaces.IVideo(block, None)
        if video is not None:
            # Re-assigning the old value updates xml metadata
            video.video = video.video
