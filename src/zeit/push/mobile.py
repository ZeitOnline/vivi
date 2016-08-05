from datetime import datetime, timedelta
from zeit.cms.i18n import MessageFactory as _
from zeit.push.interfaces import PARSE_NEWS_CHANNEL, PARSE_BREAKING_CHANNEL
import grokcore.component as grok
import logging
import pytz
import urllib
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.image.interfaces
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.cachedescriptors.property
import zope.i18n
import zope.interface


log = logging.getLogger(__name__)


class ConnectionBase(object):
    """Base class to send push notifications to mobile devices."""

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    LANGUAGE = 'de'
    PUSH_ACTION_ID = 'de.zeit.online.PUSH'

    def __init__(self, application_id, rest_api_key, expire_interval):
        self.application_id = application_id
        self.rest_api_key = rest_api_key
        self.expire_interval = expire_interval

    @zope.cachedescriptors.property.Lazy
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration(
            'zeit.push') or {}

    def get_channel_list(self, channels):
        """Return forward-compatible list of channels.

        We currently use channels as a monovalent value, set to either
        PARSE_NEWS_CHANNEL or PARSE_BREAKING_CHANNEL. Make sure to retrieve the
        according title from the config and return it as a list.

        If `channels` already is a list, just return it. This is intended for
        forward-compatibility, if we start using multiple channels.

        """
        if isinstance(channels, list):
            return channels
        return [x for x in self.config.get(channels, '').split(' ') if x]

    def get_headline(self, channels):
        """Return translation for the headline, which depends on the channel.

        Since the channel is used to classify the push notification as ordinary
        news or breaking news, it also influences the headline.

        """
        if self.config.get(PARSE_NEWS_CHANNEL) in channels:
            headline = _('parse-news-title')
        else:
            headline = _('parse-breaking-title')

        # There's no i18n in the mobile app, so we translate to a hard-coded
        # language here.
        return zope.i18n.translate(headline, target_language=self.LANGUAGE)

    @property
    def expiration_datetime(self):
        return (datetime.now(pytz.UTC).replace(microsecond=0) +
                timedelta(seconds=self.expire_interval))

    def android_data(self, title, link, channels, headline, text, supertitle):
        return {
            'action': self.PUSH_ACTION_ID,
            'headline': headline,
            'text': title,
            'teaser': text,
            'url': self.add_tracking(link, channels, 'android'),
        }

    def ios_data(self, title, link, channels, headline, text, supertitle):
        return {
            'headline': supertitle,
            'alert-title': headline,
            'alert': title,
            'teaser': text,
            'url': self.add_tracking(link, channels, 'ios'),
        }

    def data(self, title, link, **kw):
        """Return data for push notifications to Android and iOS."""
        image_url = kw.get('image_url')
        channels = self.get_channel_list(kw.get('channels'))
        if not channels:
            log.warn('No channel given for push notification for %s', link)
        arguments = {
            'title': kw.get('override_text') or kw.get('teaserTitle', title),
            'link': self.rewrite_url(link, self.config['mobile-target-host']),
            'channels': channels,
            'headline': self.get_headline(channels),
            'text': kw.get('teaserText', ''),
            'supertitle': kw.get('teaserSupertitle', ''),
        }

        data = {
            'android': self.android_data(**arguments),
            'ios': self.ios_data(**arguments)
        }

        if image_url:
            data['android']['imageUrl'] = image_url
            data['ios']['imageUrl'] = image_url

        return data

    def send(self, text, link, **kw):
        raise NotImplementedError

    @staticmethod
    def rewrite_url(url, target_host):
        is_blog = (
            url.startswith('http://blog.zeit.de') or
            url.startswith('http://www.zeit.de/blog/'))
        url = url.replace('http://www.zeit.de', target_host, 1)
        url = url.replace('http://blog.zeit.de', target_host + '/blog', 1)
        if is_blog:
            url += '?feed=articlexml'
        return url

    @staticmethod
    def add_tracking(url, channels, device):
        if PARSE_BREAKING_CHANNEL in channels:
            channel = 'eilmeldung'
        else:
            channel = 'wichtige_news'
        if device == 'android':
            device = 'andpush'
        else:
            device = 'iospush'

        tracking = {
            'wt_zmc':
            'fix.int.zonaudev.push.{channel}.zeitde.{device}.link.x'.format(
                channel=channel, device=device),
            'utm_medium': 'fix',
            'utm_source': 'push_zonaudev_int',
            'utm_campaign': channel,
            'utm_content': 'zeitde_{device}_link_x'.format(device=device),
        }
        tracking = urllib.urlencode(tracking)
        if '?' in url:
            return url + '&' + tracking
        else:
            return url + '?' + tracking


class Message(zeit.push.message.Message):

    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('mobile')

    def send_push_notification(self, service_name, **kw):
        """Overwrite to send push notifications to Parse and Urban Airship."""
        super(Message, self).send_push_notification('parse', **kw)
        super(Message, self).send_push_notification('urbanairship', **kw)

    @property
    def text(self):
        return self.context.title

    @property
    def additional_parameters(self):
        result = {}
        for name in ['teaserTitle', 'teaserText', 'teaserSupertitle']:
            value = getattr(self.context, name)
            if value:
                result[name] = value
        if self.image:
            result['image_url'] = self.image.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE,
                self.product_config['mobile-image-url'] + '/')
        return result

    @property
    def image(self):
        images = zeit.content.image.interfaces.IImages(self.context, None)
        if images is None or images.image is None:
            return None
        image = images.image
        if zeit.content.image.interfaces.IImageGroup.providedBy(image):
            for name in image:
                if self._image_pattern in name:
                    return image[name]
        else:
            return image

    @property
    def _image_pattern(self):
        return self.product_config['parse-image-pattern']

    @zope.cachedescriptors.property.Lazy
    def product_config(self):
        return zope.app.appsetup.product.getProductConfiguration('zeit.push')


class ParseMessage(Message):
    """Also register the mobile message under the name `parse` for bw compat.

    Since the message config is stored on the article, there are many articles
    that contain a message config for `parse`. To make sure those messages are
    send to Parse (bw-compat) & Urban Airship (fw-compat), we need to register
    the new `mobile` message also under the old name `parse`.

    """

    grok.name('parse')


@grok.subscribe(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def set_push_news_flag(context, event):
    push = zeit.push.interfaces.IPushMessages(context)
    for service in push.message_config:
        if (service['type'] in ['mobile', 'parse'] and
                service.get('enabled') and
                service.get('channels') == PARSE_NEWS_CHANNEL):
            context.push_news = True
            break
