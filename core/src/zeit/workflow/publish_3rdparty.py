import datetime
import grokcore.component as grok
import logging
import time
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
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow') or {}
        ignore_ressorts = set(
            x.strip().lower()
            for x in config.get(
                'facebooknewstab-ignore-ressorts', '').split(','))
        ressort = self.context.ressort
        if ressort.lower() in ignore_ressorts:
            return
        product_id = self.context.product.id
        ignore_products = set(
            x.strip().lower()
            for x in config.get(
                'facebooknewstab-ignore-products', '').split(','))
        if product_id.lower() in ignore_products:
            return
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        date_first_released = info.date_first_released
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


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class Speechbert(grok.Adapter):
    grok.context(zeit.content.article.interfaces.IArticle)
    grok.name('speechbert')

    def ignore(self, date_first_released):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow') or {}
        max_age = int(config['speechbert-max-age'])
        if (time.time() - date_first_released.float_timestamp) >= max_age:
            return True
        ignore_genres = [
            x.lower() for x in config['speechbert-ignore-genres'].split()]
        genre = self.context.genre
        if genre and genre.lower() in ignore_genres:
            return True
        ignore_templates = [
            x.lower() for x in config['speechbert-ignore-templates'].split()]
        template = self.context.template
        if template.lower() in ignore_templates:
            return True
        return False

    def json(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        if self.ignore(info.date_first_released):
            return
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        result = {
            'uuid': uuid.shortened,
            'unique_id': self.context.uniqueId}
        payload = result['payload'] = {}
        if self.context.access != 'free':
            payload['access'] = self.context.access
        head = getattr(self.context.xml, 'head')
        # TODO there is a "not(role)" check in the original XSLT
        payload['authors'] = [
            x.display_name for x in head.findall('author')]
        body = payload['body'] = []
        elements = self.context.body.xml.xpath(
            "(//division/* | //division/ul/*)")
        for elem in elements:
            if elem.tag not in ('intertitle', 'li', 'p'):
                continue
            if elem.text is not None:
                body.append(dict(
                    content=elem.text,
                    type=elem.tag))
            else:
                text = elem.findtext('**')
                if text is None:
                    text = elem.findtext('*')
                body.append(dict(
                    content=text,
                    type=elem.tag))
        if self.context.channels:
            payload['channels'] = ' '.join(*self.context.channels)
        if self.context.genre:
            payload['genre'] = self.context.genre
        if self.context.audio_speechbert:
            payload['hasAudio'] = True
        payload['headline'] = self.context.title
        image_url = self.context.main_image.source.xml.attrib.get('base-id')
        if image_url:
            payload['image'] = image_url.replace(
                zeit.cms.interfaces.ID_NAMESPACE,
                'https://img.zeit.de/').rstrip('/') + '/wide__820x461__desktop'
        if info.date_last_published_semantic is not None:
            payload['lastModified'] = (
                info.date_last_published_semantic.isoformat())
        if info.date_first_released is not None:
            payload['publishDate'] = info.date_first_released.isoformat()
        payload['section'] = self.context.ressort
        if self.context.serie:
            payload['series'] = self.context.serie.serienname
        if self.context.sub_ressort:
            payload['subsection'] = self.context.sub_ressort
        if self.context.subtitle:
            payload['subtitle'] = self.context.subtitle
        if self.context.supertitle:
            payload['supertitle'] = self.context.supertitle
        payload['tags'] = []
        if hasattr(head, 'rankedTags'):
            payload['tags'].extend(
                self.context.xml.head.rankedTags.getchildren())
        payload['teaser'] = self.context.teaserText
        payload['url'] = ''
        if uuid.shortened:
            payload['uuid'] = uuid.shortened
        return result
