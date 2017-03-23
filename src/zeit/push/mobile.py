from datetime import datetime, timedelta
from zeit.cms.i18n import MessageFactory as _
from zeit.push.interfaces import CONFIG_CHANNEL_NEWS, CONFIG_CHANNEL_BREAKING
import grokcore.component as grok
import logging
import pytz
import urllib
import urlparse
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.image.interfaces
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.cachedescriptors.property
import zope.component
import zope.i18n
import zope.interface


log = logging.getLogger(__name__)


class ConnectionBase(object):
    """Base class to send push notifications to mobile devices."""

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    LANGUAGE = 'de'
    APP_IDENTIFIER = 'zeitapp'

    def __init__(self, expire_interval):
        self.expire_interval = expire_interval

    @zope.cachedescriptors.property.Lazy
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration(
            'zeit.push') or {}

    def get_channel_list(self, channels):
        """Return forward-compatible list of channels.

        We currently use channels as a monovalent value, set to either
        CONFIG_CHANNEL_NEWS or CONFIG_CHANNEL_BREAKING. Make sure to retrieve
        the according title from the config and return it as a list.

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
        if self.config.get(CONFIG_CHANNEL_NEWS) in channels:
            return None
        else:
            headline = _('push-breaking-title')

        # There's no i18n in the mobile app, so we translate to a hard-coded
        # language here.
        return zope.i18n.translate(headline, target_language=self.LANGUAGE)

    @property
    def expiration_datetime(self):
        return (datetime.now(pytz.UTC).replace(microsecond=0) +
                timedelta(seconds=self.expire_interval))

    def data(self, title, link, **kw):
        """Return data for push notifications to Android and iOS."""
        channels = self.get_channel_list(kw.get('channels'))
        if not channels:
            log.warn('No channel given for push notification for %s', link)

        is_breaking = self.config.get(CONFIG_CHANNEL_BREAKING) in channels

        # Extra tag helps the app know which kind of notification was send
        if is_breaking:
            extra_tag = self.config.get(CONFIG_CHANNEL_BREAKING)
        else:
            extra_tag = self.config.get(CONFIG_CHANNEL_NEWS)

        path = self.strip_to_path(link)
        push_target = self.config.get('push-target-url', '').rstrip('/')
        full_link = '/'.join((push_target, path))
        deep_link = '://'.join((self.APP_IDENTIFIER, path))

        headline = self.get_headline(channels)
        return {
            'ios': {
                'alert': title,
                'deep_link': self.add_tracking(deep_link, channels, 'ios'),
                'headline': headline,
                'sound': 'chime.aiff' if is_breaking else '',
                'tag': extra_tag,
                'url': self.add_tracking(full_link, channels, 'ios')
            },
            'android': {
                'alert': title,
                'deep_link': self.add_tracking(deep_link, channels, 'android'),
                'headline': 'ZEIT ONLINE {}'.format(
                    headline) if headline else None,
                'priority': 2 if is_breaking else 0,
                'tag': extra_tag,
                'url': self.add_tracking(full_link, channels, 'android')
            }
        }

    def send(self, text, link, **kw):
        raise NotImplementedError

    @staticmethod
    def strip_to_path(url):
        if '://' not in url:
            url = '//' + url.lstrip('/')  # ensure valid url
        return urlparse.urlunparse(
            ['', ''] + list(urlparse.urlparse(url)[2:])).lstrip('/')

    @staticmethod
    def add_tracking(url, channels, device):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push') or {}
        if config.get(CONFIG_CHANNEL_BREAKING) in channels:
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

        tracking_query = urllib.urlencode(tracking)
        parsed_url = list(urlparse.urlparse(url))  # ParseResult is immutable
        parsed_url[4] = '&'.join((parsed_url[4], tracking_query))
        return urlparse.urlunparse(parsed_url)


class Message(zeit.push.message.Message):

    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('mobile')

    def send_push_notification(self, service_name, **kw):
        # BBB This used to send to both parse and urbanairship, so we use
        # a generic name in the message_config.
        super(Message, self).send_push_notification('urbanairship', **kw)

    def log_success(self, name):
        message = (
            self.config.get('override_text') or
            self.additional_parameters.get('teaserTitle') or
            self.text)

        notifier = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name=name)
        channels = notifier.get_channel_list(self.config.get('channels'))

        self.object_log.log(_(
            'Push notification for "${name}" sent. '
            '(Message: "${message}", Channels: ${channels})',
            mapping={
                'name': name.capitalize(),
                'message': message,
                'channels': ' '.join(channels)}))

    @zope.cachedescriptors.property.Lazy
    def text(self):
        return self.config.get('override_text', self.context.title)

    @zope.cachedescriptors.property.Lazy
    def additional_parameters(self):
        result = {}
        for name in ['teaserTitle', 'teaserText', 'teaserSupertitle']:
            value = getattr(self.context, name)
            if value:
                result[name] = value
        if self.image:
            result['image_url'] = self.image.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE,
                self.product_config['mobile-image-url'])
        return result

    @property
    def image(self):
        images = zeit.content.image.interfaces.IImages(self.context, None)
        return getattr(images, 'image', None)

    @zope.cachedescriptors.property.Lazy
    def product_config(self):
        return zope.app.appsetup.product.getProductConfiguration('zeit.push')


@grok.subscribe(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def set_push_news_flag(context, event):
    push = zeit.push.interfaces.IPushMessages(context)
    for service in push.message_config:
        if (service['type'] == 'mobile' and
                service.get('enabled') and
                service.get('channels') == CONFIG_CHANNEL_NEWS):
            context.push_news = True
            break
