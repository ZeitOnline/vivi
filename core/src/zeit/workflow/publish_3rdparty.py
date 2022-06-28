import datetime
import grokcore.component as grok
import logging
import zope.app.appsetup.product
import zeit.cms.content.interfaces
import zeit.cms.interfaces
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


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class FacebookNewstab(grok.Adapter):
    grok.context(zeit.content.article.interfaces.IArticleMetadata)
    grok.name('facebooknewstab')

    CONTENT_TYPES = frozenset([
        'article',
    ])

    def json(self):
        content_type = zeit.cms.type.get_type(self.context)
        if content_type not in self.CONTENT_TYPES:
            # we want to prevent this being called for content types
            # which don't need comments, so emit a warning
            log.warning(
                "Got content_type %r for facebooknewstab, "
                "check adapter registration for FacebookNewstab.",
                content_type)
            return
        ressort = self.context.ressort
        if ressort == "Administratives":
            # ignore resources with this ressort
            return
        product_id = self.context.product.id
        if product_id in ("ADV", "VAB"):
            # ignore resources with these product ids
            return
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        date_first_released = info.date_first_released
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow') or {}
        facebooknewstab_startdate = datetime.datetime.strptime(
            config['facebooknewstab-startdate'],
            "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        if date_first_released < facebooknewstab_startdate:
            # ignore resources before the cut off date
            return
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        # TODO does this setting exist under a different name already?
        live_prefix = config['facebooknewstab-live-prefix']
        live_url = self.context.uniqueId
        if live_url.startswith(zeit.cms.interfaces.ID_NAMESPACE):
            # TODO with Python >= 3.9 we can use:
            # live_url = live_url.removeprefix(
            #     zeit.cms.interfaces.ID_NAMESPACE)
            live_url = live_url[len(zeit.cms.interfaces.ID_NAMESPACE):]
            live_url = f'{live_prefix}{live_url}'
        return {
            'uuid': uuid.shortened,
            'unique_id': self.context.uniqueId,
            'live_url': live_url}
