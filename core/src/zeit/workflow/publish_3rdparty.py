from itertools import chain
import logging

import grokcore.component as grok
import lxml.etree
import pendulum
import zope.component

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.config
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.video.interfaces
import zeit.objectlog.interfaces
import zeit.retresco.interfaces
import zeit.workflow.interfaces


log = logging.getLogger(__name__)


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class Airship(grok.Adapter):
    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('airship')

    def publish_json(self):
        if not FEATURE_TOGGLES.find('push_airship_via_publisher'):
            return None

        message = None
        info = zeit.push.interfaces.IPushMessages(self.context)
        for config in info.message_config:
            if config['type'] == 'mobile' and config.get('enabled'):
                message = info._create_message(config['type'], self.context, config)
                # This assumes there ever can be only one airship config,
                # even though the data structure would allow for multiple.
                break
        if message is None:
            return None

        # Prevent calling Airship more than once. NOTE: This is a write in an
        # otherwise reading operation. But this is pretty much the only spot to
        # do this, because here we can rely the fact that there has to be a
        # commit before publisher is called. If that commit succeeds, the
        # disabling is persisted, no matter what else happens afterwards
        # (airship errors, zodb conflict errors, etc). And if that commit
        # fails, publisher (and thus Airship) is not called.
        info.set(message.config, enabled=False)

        kind = message.config.get('payload_template', 'unknown')
        # XXX Stopgap so the user gets _some_ kind of feedback. But of course,
        # the Airship call has not actually happened yet, and if an error
        # occurs, the user currently will not be told about it.
        zeit.objectlog.interfaces.ILog(self.context).log(
            _(
                'Push notification for "${name}" sent.'
                ' (Message: "${message}", Details: ${details})',
                mapping={
                    'name': 'Airship',
                    'message': message.text,
                    'details': f'Template {kind}',
                },
            )
        )

        return {
            'kind': kind,
            'pushes': self._absolute_expiry(message.render()),
        }

    def _absolute_expiry(self, pushes):
        expire_interval = int(zeit.cms.config.required('zeit.push', 'urbanairship-expire-interval'))

        now = pendulum.now()
        # See https://docs.urbanairship.com/api/ua/#schemas-pushobject
        for push in pushes:
            expiry = push.setdefault('options', {}).setdefault('expiry', expire_interval)
            # We transmit an absolute timestamp, not relative seconds, as a
            # safetybelt against (very) delayed pushes. The format must not
            # contain microseconds, so no `isoformat`.
            expiry = now.add(seconds=expiry)
            push['options']['expiry'] = expiry.strftime('%Y-%m-%dT%H:%M:%S')
        return pushes

    def retract_json(self):
        return None


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


class LiveUrlMixin:
    @property
    def live_url(self):
        live_prefix = zeit.cms.config.required('zeit.cms', 'live-prefix')
        return self.context.uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE, live_prefix)


class BigQueryMixin(LiveUrlMixin):
    def publish_json(self):
        tms = zeit.retresco.interfaces.ITMSRepresentation(self.context)()
        if tms is None:
            return None
        properties = tms.get('payload', {})
        properties.setdefault('meta', {})['url'] = self.live_url
        properties['tagging'] = {k: v for k, v in tms.items() if k.startswith('rtr_')}
        return {
            'properties': properties,
            'body': badgerfish(self.context.xml.find('body'))['body'],
        }

    def retract_json(self):
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        return {
            'properties': {
                'meta': {'url': self.live_url},
                'document': {'uuid': uuid.id},
            }
        }


def badgerfish(node):
    """Adapted from http://www.sklar.com/badgerfish/, with changes:
    * 7.-9. namespaces are simply removed from both tag and attribute names
    * Nodes with mixed content (text and child tags) only return the collected
      text and no child nodes
    """
    result = {}
    children = list(node.iterchildren())

    node_text = node.text.strip() if node.text else False
    if children and (node_text or any(x.tail.strip() for x in children if x.tail)):
        result['$'] = ' '.join([x.strip() for x in node.xpath('.//text()')])
        children = []
    elif node_text:
        result['$'] = node_text

    for key, value in node.attrib.items():
        key = lxml.etree.QName(key).localname
        result[f'@{key}'] = value

    for child in children:
        # https://lxml.de/FAQ.html#how-can-i-find-out-if-an-element-is-a-comment-or-pi
        if not isinstance(child.tag, str):
            continue

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

    @property
    def live_url(self):
        live_prefix = zeit.cms.config.required('zeit.cms', 'live-prefix')
        return self.context.live_url_base.replace(zeit.cms.interfaces.ID_NAMESPACE, live_prefix)


class CommentsMixin:
    def publish_json(self):
        return {
            'comments_allowed': self.context.commentsAllowed,
            'pre_moderated': self.context.commentsPremoderate,
            'type': 'commentsection',
            'visible': self.context.commentSectionEnable,
        }

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


class IgnoreMixin:
    """Ignore publish/retract based on settings."""

    #: map article attributes to settings
    attr_setting_mapping = {
        'genre': 'genres',
        'template': 'templates',
        'ressort': 'ressorts',
    }

    @property
    def name(self):
        """defined with grok.name"""
        return self.__class__.__dict__['grokcore.component.directive.name']

    def ignore(self, method):
        if self.context.product and self.context.product.is_news:
            return True
        if method == 'publish':
            for attribute, setting in self.attr_setting_mapping.items():
                if self.is_on_ignorelist(attribute, setting):
                    return True
        return False

    def is_on_ignorelist(self, attribute, setting):
        ignore_list = (
            zeit.cms.config.get('zeit.workflow', f'{self.name}-ignore-{setting}', '')
            .lower()
            .split()
        )
        value = getattr(self.context, attribute)
        return value and value.lower() in ignore_list

    def publish_json(self):
        if self.ignore('publish'):
            return None
        return self._json()

    def retract_json(self):
        if self.ignore('retract'):
            return None
        return {}


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class Speechbert(grok.Adapter, IgnoreMixin):
    grok.context(zeit.content.article.interfaces.IArticle)
    grok.name('speechbert')

    def get_image(self):
        image = zeit.content.image.interfaces.IImages(self.context).image
        if not image:
            return None
        prefix = zeit.cms.config.get('zeit.cms', 'image-live-prefix', '').strip('/')
        variant_url = image.variant_url('')  # ZO-2856: no slug
        if not variant_url:
            return None
        return f'{prefix}{variant_url}'

    def _json(self):
        checksum = zeit.content.article.interfaces.ISpeechbertChecksum(self.context)
        payload = {
            'authors': [x.target.display_name for x in self.context.authorships if not x.role],
            'body': self.context.get_body(),
            'checksum': checksum.checksum,
            'channels': ' '.join([x for x in chain(*self.context.channels) if x]),
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
            payload['lastModified'] = info.date_last_published_semantic.isoformat()
        if info.date_first_released is not None:
            payload['publishDate'] = info.date_first_released.isoformat()
        if self.context.serie:
            payload['series'] = self.context.serie.serienname
        return {k: v for k, v in payload.items() if v}


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
            # must wait for elastic index update before invalidating fastly cache
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
class Summy(grok.Adapter, IgnoreMixin):
    grok.context(zeit.content.article.interfaces.IArticle)
    grok.name('summy')

    def _json(self):
        return {
            'text': self.context.get_body(),
            'avoid_create_summary': self.context.avoid_create_summary,
        }

    def publish_json(self):
        if self.ignore('publish'):
            # this is explicitly set to empty dict
            # because we still want to notify summy
            # and summy will store some additional values
            # even though it does not create a summary
            return {}
        return self._json()

    def retract_json(self):
        return {}


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class PublisherData(grok.Adapter):
    grok.context(zeit.cms.interfaces.ICMSContent)

    ignore = ()  # extension point e.g. for bulk publish scripts

    def __call__(self, action):
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        result = {'uuid': uuid.shortened, 'uniqueId': self.context.uniqueId}
        for name, adapter in zope.component.getAdapters(
            (self.context,), zeit.workflow.interfaces.IPublisherData
        ):
            if not name:  # ourselves
                continue
            if self._ignore(name):
                continue
            data = getattr(adapter, f'{action}_json')()
            if data is not None:
                result[name] = data
        return result

    def _ignore(self, name):
        if name in self.ignore:
            return True
        if FEATURE_TOGGLES.find(f'disable_publisher_{name}'):
            return True
        return False


class IndexNowMixin(LiveUrlMixin):
    def publish_json(self):
        return {'url': self.live_url}

    def retract_json(self):
        return None


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class ArticleIndexNow(grok.Adapter, IndexNowMixin):
    grok.context(zeit.content.article.interfaces.IArticle)
    grok.name('indexnow')


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class CenterPageIndexNow(grok.Adapter, IndexNowMixin):
    grok.context(zeit.content.cp.interfaces.ICenterPage)
    grok.name('indexnow')
