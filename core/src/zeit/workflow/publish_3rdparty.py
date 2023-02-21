from itertools import chain
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
import zeit.content.image.interfaces
import zeit.content.video.interfaces
import zeit.workflow.interfaces


log = logging.getLogger(__name__)


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class AuthorDashboard(grok.Adapter):
    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('authordashboard')

    def publish_json(self):
        # no payload. uuid and uniqueId are passed in automatically
        return {}

    def retract_json(self):
        # on retraction nothing is done
        return None


class BigQueryMixin:
    PREFIX = zeit.cms.interfaces.ID_NAMESPACE.rstrip('/')

    def publish_json(self):
        path = self.context.uniqueId.removeprefix(self.PREFIX)
        return {'path': path}

    def retract_json(self):
        return self.publish_json()


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
    def publish_json(self):
        # the uuid and unique_id are required in the payload,
        # since the publisher should have no logic in that regard,
        # we duplicate the two here
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        return {
            'comments_allowed': self.context.commentsAllowed,
            'pre_moderated': self.context.commentsPremoderate,
            'type': 'commentsection',
            'uuid': uuid.shortened,
            'unique_id': self.context.uniqueId,
            'visible': self.context.commentSectionEnable}

    def retract_json(self):
        # on retraction nothing is done
        return None


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

    PREFIX = zeit.cms.interfaces.ID_NAMESPACE.rstrip('/')

    def publish_json(self):
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
        if date_first_released is not None:
            if date_first_released < facebooknewstab_startdate:
                # ignore resources before the cut off date
                return
        path = self.context.uniqueId.removeprefix(self.PREFIX)
        return {'path': path}

    def retract_json(self):
        return self.publish_json()


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class Speechbert(grok.Adapter):
    grok.context(zeit.content.article.interfaces.IArticle)
    grok.name('speechbert')

    def ignore(self, method):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow') or {}
        if method == "publish":
            ignore_genres = [
                x.lower()
                for x in config['speechbert-ignore-genres'].split()]
            genre = self.context.genre
            if genre and genre.lower() in ignore_genres:
                return True
        if method == "publish":
            ignore_templates = [
                x.lower()
                for x in config['speechbert-ignore-templates'].split()]
            template = self.context.template
            if template is not None and template.lower() in ignore_templates:
                return True
        return False

    def get_body(self):
        body = []
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
                if text is None:
                    continue
                body.append(dict(
                    content=text,
                    type=elem.tag))
        return body

    def get_image(self):
        image = zeit.content.image.interfaces.IImages(self.context).image
        if not image:
            return
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms') or {}
        prefix = config.get('image-live-prefix', '').strip('/')
        variant_url = image.variant_url('wide', width=820, height=461)
        if not variant_url:
            return
        return f'{prefix}{variant_url}'

    def _json(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms') or {}
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        payload = dict(
            authors=[x.target.display_name for x in self.context.authorships
                     if not x.role],
            body=self.get_body(),
            channels=' '.join([x for x in chain(*self.context.channels) if x]),
            genre=self.context.genre,
            hasAudio='true' if self.context.audio_speechbert else 'false',
            headline=self.context.title,
            image=self.get_image(),
            section=self.context.ressort,
            subsection=self.context.sub_ressort,
            subtitle=self.context.subtitle,
            supertitle=self.context.supertitle,
            tags=[x.label for x in self.context.keywords],
            teaser=self.context.teaserText,
            url=self.context.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE, config['live-prefix']),
            uuid=uuid.shortened)
        if self.context.access != 'free':
            payload['access'] = self.context.access
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        if info.date_last_published_semantic is not None:
            payload['lastModified'] = (
                info.date_last_published_semantic.isoformat())
        if info.date_first_released is not None:
            payload['publishDate'] = info.date_first_released.isoformat()
        if self.context.serie:
            payload['series'] = self.context.serie.serienname
        return {k: v for k, v in payload.items() if v}

    def publish_json(self):
        if self.ignore('publish'):
            return
        return self._json()

    def retract_json(self):
        if self.ignore('retract'):
            return
        return {
            # Can we simplify this protocol? uuid is already passed in toplevel
            # so we should not have to repeat it here.
            'uuid': zeit.cms.content.interfaces.IUUID(self.context).shortened
        }
