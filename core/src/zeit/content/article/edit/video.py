import grokcore.component as grok
import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.reference
import zeit.content.video.interfaces
import zeit.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IVideo)
class Video(zeit.content.article.edit.reference.Reference):
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

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        if self.layout is None:
            self.layout = zeit.content.article.edit.interfaces.IVideo['layout'].default

    @property
    def video(self):  # BBB for zeit.web
        return self.references


class Factory(zeit.content.article.edit.reference.ReferenceFactory):
    produces = Video
    title = _('Video')


@grok.adapter(
    zeit.content.article.edit.interfaces.IArticleArea,
    zeit.content.video.interfaces.IVideo,
    int,
)
@grok.implementer(zeit.edit.interfaces.IElement)
def create_video_block_from_video(body, context, position):
    block = Factory(body)(position)
    block.references = context
    return block
