import grokcore.component as grok
import logging


import zeit.cms.content.interfaces
import zeit.cms.type
import zeit.content.article.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces
import zeit.workflow.interfaces


log = logging.getLogger(__name__)


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class AuthorDashboard(grok.Adapter):
    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('authordashboard')

    def json(self):
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        return {
            'uuid': uuid.shortened,
            'unique_id': self.context.uniqueId}


class CommentsMixin:

    CONTENT_TYPES = frozenset([
        'article',
        'gallery',
        'video',
    ])

    def json(self):
        content_type = zeit.cms.type.get_type(self.context)
        if content_type not in self.CONTENT_TYPES:
            # we want to prevent this being called for content types
            # which don't need comments, so emit a warning
            log.warning(
                "Got content_type %r for comments, "
                "check adapter registration for Comments.",
                content_type)
            return
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        return {
            'comments_allowed': self.context.commentsAllowed,
            'pre_moderated': self.context.commentsPremoderate,
            'type': 'commentsection',
            'uuid': uuid.shortened,
            'unique_id': self.context.uniqueId,
            'visible': self.context.commentSectionEnable}


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class ArticleComments(grok.Adapter, CommentsMixin):
    grok.context(zeit.content.article.interfaces.IArticleMetadata)
    grok.name('comments')


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class GalleryComments(grok.Adapter, CommentsMixin):
    grok.context(zeit.content.gallery.interfaces.IGalleryMetadata)
    grok.name('comments')


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class VideoComments(grok.Adapter, CommentsMixin):
    grok.context(zeit.content.video.interfaces.IVideo)
    grok.name('comments')
