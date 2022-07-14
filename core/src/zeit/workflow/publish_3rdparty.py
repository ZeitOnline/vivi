import datetime
import grokcore.component as grok
import logging
import zope.app.appsetup.product
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
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


class BigQueryMixin:
    PREFIX = zeit.cms.interfaces.ID_NAMESPACE.rstrip('/')

    def json(self):
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        path = self.context.uniqueId
        # TODO with Python >= 3.9 we can use:
        # path = self.context.uniqueId.removeprefix(self.PREFIX)
        if path.startswith(self.PREFIX):
            path = path[len(self.PREFIX):]
        return {
            'uuid': uuid.shortened,
            'unique_id': self.context.uniqueId,
            'path': path}


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class ArticleBigQuery(grok.Adapter, BigQueryMixin):
    grok.context(zeit.content.article.interfaces.IArticle)
    grok.name('bigquery')


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class CenterPageBigQuery(grok.Adapter, BigQueryMixin):
    grok.context(zeit.content.cp.interfaces.ICenterPage)
    grok.name('bigquery')


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class GalleryBigQuery(grok.Adapter, BigQueryMixin):
    grok.context(zeit.content.gallery.interfaces.IGallery)
    grok.name('bigquery')


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class VideoBigQuery(grok.Adapter, BigQueryMixin):
    grok.context(zeit.content.video.interfaces.IVideo)
    grok.name('bigquery')


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
    grok.context(zeit.content.article.interfaces.IArticle)
    grok.name('comments')


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class GalleryComments(grok.Adapter, CommentsMixin):
    grok.context(zeit.content.gallery.interfaces.IGallery)
    grok.name('comments')


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class VideoComments(grok.Adapter, CommentsMixin):
    grok.context(zeit.content.video.interfaces.IVideo)
    grok.name('comments')


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class FacebookNewstab(grok.Adapter):
    grok.context(zeit.content.article.interfaces.IArticle)
    grok.name('facebooknewstab')

    CONTENT_TYPES = frozenset([
        'article',
    ])

    PREFIX = zeit.cms.interfaces.ID_NAMESPACE.rstrip('/')

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
        path = self.context.uniqueId
        # TODO with Python >= 3.9 we can use:
        # path = self.context.uniqueId.removeprefix(self.PREFIX)
        if path.startswith(self.PREFIX):
            path = path[len(self.PREFIX):]
        return {
            'uuid': uuid.shortened,
            'unique_id': self.context.uniqueId,
            'path': path}
