from itertools import chain
from zeit.cms.content.sources import FEATURE_TOGGLES
import datetime
import grokcore.component as grok
import logging
import lxml.etree
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.video.interfaces
import zeit.retresco.interfaces
import zeit.workflow.interfaces
import zope.app.appsetup.product


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

    def publish_json(self):
        if not FEATURE_TOGGLES.find('publish_bigquery_json'):
            return {}
        tms = zeit.retresco.interfaces.ITMSRepresentation(self.context)()
        if tms is None:
            return None
        properties = tms.get('payload', {})
        properties.setdefault('meta', {})['url'] = self.context.uniqueId
        properties['tagging'] = {
            k: v for k, v in tms.items() if k.startswith('rtr_')}
        return {
            'properties': properties,
            'body': badgerfish(self.context.xml.body)['body'],
        }

    def retract_json(self):
        if not FEATURE_TOGGLES.find('publish_bigquery_json'):
            return {}
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        return {'properties': {
            'meta': {'url': self.context.uniqueId},
            'document': {'uuid': uuid.id},
        }}


def badgerfish(node):
    """Adapted from http://www.sklar.com/badgerfish/, with changes:
    * 7.-9. namespaces are simply removed from both tag and attribute names
    * Nodes with mixed content (text and child tags) only return the collected
      text and no child nodes
    """
    result = {}
    children = list(node.iterchildren())

    if node.text:
        if not children:
            result['$'] = node.text
        else:
            result['$'] = ' '.join(
                [x.strip() for x in node.xpath('.//text()')])
            children = []

    for key, value in node.attrib.items():
        key = lxml.etree.QName(key).localname
        result[f'@{key}'] = value

    for child in children:
        child_tag = lxml.etree.QName(child.tag).localname
        sub = badgerfish(child)[child_tag]
        existing = result.get(child_tag)
        if existing is None:
            result[child_tag] = sub
        elif isinstance(existing, list):
            existing.append(sub)
        else:
            result[child.tag] = [existing, sub]

    return {lxml.etree.QName(node.tag).localname: result}


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
        return {
            'comments_allowed': self.context.commentsAllowed,
            'pre_moderated': self.context.commentsPremoderate,
            'type': 'commentsection',
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

    def publish_json(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow') or {}
        ignore_ressorts = {
            x.strip().lower()
            for x in config.get(
                'facebooknewstab-ignore-ressorts', '').split(',')}
        ressort = self.context.ressort
        if ressort.lower() in ignore_ressorts:
            return None
        product_id = self.context.product.id
        ignore_products = {
            x.strip().lower()
            for x in config.get(
                'facebooknewstab-ignore-products', '').split(',')}
        if product_id.lower() in ignore_products:
            return None
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        date_first_released = info.date_first_released
        facebooknewstab_startdate = datetime.datetime.strptime(
            config['facebooknewstab-startdate'],
            "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        if date_first_released is not None:
            if date_first_released < facebooknewstab_startdate:
                # Ignore resources before the cut off date.
                return None
        return {}

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
        if self.context.product and self.context.product.is_news:
            return True
        return False

    def get_body(self):
        body = []
        elements = self.context.body.xml.xpath(
            "(//division/* | //division/ul/*)")
        for elem in elements:
            if elem.tag not in ('intertitle', 'li', 'p'):
                continue
            text = elem.xpath('.//text()')
            if not text:
                continue
            body.append({
                'content': ' '.join([x.strip() for x in text]),
                'type': elem.tag})
        return body

    def get_image(self):
        image = zeit.content.image.interfaces.IImages(self.context).image
        if not image:
            return None
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms') or {}
        prefix = config.get('image-live-prefix', '').strip('/')
        variant_url = image.variant_url('')  # ZO-2856: no slug
        if not variant_url:
            return None
        return f'{prefix}{variant_url}'

    def _json(self):
        checksum = zeit.content.article.interfaces.ISpeechbertChecksum(
            self.context)
        payload = {
            'authors': [x.target.display_name for x in self.context.authorships
                        if not x.role],
            'body': self.get_body(),
            'checksum': checksum.checksum,
            'channels': ' '.join([
                x for x in chain(*self.context.channels) if x]),
            'genre': self.context.genre,
            'hasAudio': 'true' if self.context.audio_speechbert else 'false',
            'headline': self.context.title,
            'image': self.get_image(),
            'section': self.context.ressort,
            'subsection': self.context.sub_ressort,
            'subtitle': self.context.subtitle,
            'supertitle': self.context.supertitle,
            'tags': [x.label for x in self.context.keywords],
            'teaser': self.context.teaserText,
        }
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
            return None
        return self._json()

    def retract_json(self):
        if self.ignore('retract'):
            return None
        return {}


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class TMS(grok.Adapter):
    grok.context(zeit.cms.interfaces.ICMSContent)
    grok.name('tms')

    def ignore(self):
        if zeit.retresco.interfaces.ITMSRepresentation(self.context)() is None:
            return True
        return False

    def wait_for_index_update(self):
        if zeit.content.article.interfaces.IArticle.providedBy(self.context):
            # TMS supplies article body intext links, therefore publish process
            # must wait for elastic index update
            return True
        return False

    def publish_json(self):
        if self.ignore():
            return None
        return {'wait': self.wait_for_index_update()}

    def retract_json(self):
        if self.ignore():
            return None
        return {}


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class PublisherData(grok.Adapter):
    grok.context(zeit.cms.interfaces.ICMSContent)

    ignore = ()  # extension point e.g. for bulk publish scripts

    def __call__(self, action):
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        result = {'uuid': uuid.shortened, 'uniqueId': self.context.uniqueId}
        for name, adapter in zope.component.getAdapters(
                (self.context,), zeit.workflow.interfaces.IPublisherData):
            if not name:  # ourselves
                continue
            if name in self.ignore:
                continue
            data = getattr(adapter, f'{action}_json')()
            if data is not None:
                result[name] = data
        return result
