# Why is this needed?
from __future__ import absolute_import

from datetime import datetime, timedelta
from zeit.cms.i18n import MessageFactory as _
from zeit.push.interfaces import CONFIG_CHANNEL_NEWS, CONFIG_CHANNEL_BREAKING
import collections
import grokcore.component as grok
import json
import logging
import pytz
import urbanairship
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


class Connection(object):
    """Class to send push notifications to mobile devices via urbanairship."""

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    LANGUAGE = 'de'
    APP_IDENTIFIER = 'zeitapp'

    def __init__(self, android_application_key, android_master_secret,
                 ios_application_key, ios_master_secret, expire_interval):
        self.android_application_key = android_application_key
        self.android_master_secret = android_master_secret
        self.ios_application_key = ios_application_key
        self.ios_master_secret = ios_master_secret
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
            headline = _('push-news-title')
        else:
            headline = _('push-breaking-title')

        # There's no i18n in the mobile app, so we translate to a hard-coded
        # language here.
        return zope.i18n.translate(headline, target_language=self.LANGUAGE)

    @property
    def expiration_datetime(self):
        return (datetime.now(pytz.UTC).replace(microsecond=0) +
                timedelta(seconds=self.expire_interval))

    def create_payload(self, text, link, **kw):
        channels = self.get_channel_list(kw.get('channels'))
        parts = urlparse.urlparse(link)
        path = urlparse.urlunparse(['', ''] + list(parts[2:])).lstrip('/')
        full_link = u'%s://%s/%s' % (parts.scheme, parts.netloc, path)
        deep_link = u'%s://%s' % (self.APP_IDENTIFIER, path)
        android_headline = 'ZEIT ONLINE {}'.format(self.get_headline(channels))

        is_breaking = self.config.get(CONFIG_CHANNEL_BREAKING) in channels
        # Extra tag helps the app know which kind of notification was send
        if is_breaking:
            extra_tag = self.config.get(CONFIG_CHANNEL_BREAKING)
        else:
            extra_tag = self.config.get(CONFIG_CHANNEL_NEWS)

        return {
            'android': {
                'actions': {
                    'open': {
                        'type': 'deep_link',
                        'content': self.add_tracking(
                            deep_link, channels, 'android')
                    }
                },
                'alert': text,
                'android': {
                    'extra': {
                        'headline': android_headline,
                        'tag': extra_tag,
                        'url': self.add_tracking(
                            full_link, channels, 'android')
                    },
                    'priority': 2 if is_breaking else 0,
                    'title': android_headline,
                }
            },
            'ios': {
                'actions': {
                    'open': {
                        'type': 'deep_link',
                        'content': self.add_tracking(
                            deep_link, channels, 'ios')
                    }
                },
                'alert': text,
                'ios': {
                    'extra': {
                        'headline': self.get_headline(channels),
                        'tag': extra_tag,
                        'url': self.add_tracking(full_link, channels, 'ios')
                    },
                    'sound': 'chime.aiff' if is_breaking else '',
                    'title': self.get_headline(channels),
                }
            }
        }

    def send(self, text, link, **kw):
        channels = self.get_channel_list(kw.get('channels'))
        if not channels:
            raise ValueError('No channel given to define target audience.')

        # We need channels to define the target audience in order to avoid
        # accidental pushes to *all* devices.
        audience_channels = {
            'OR': [{'group': self.config['urbanairship-audience-group'],
                    'tag': channel} for channel in channels],
        }

        # The expiration datetime must not contain microseconds, therefore we
        # cannot use `isoformat`.
        expiry = self.expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        payload = self.create_payload(text, link, **kw)

        # Send android notification.
        android = urbanairship.Airship(
            self.android_application_key,
            self.android_master_secret
        ).create_push()
        android.audience = audience_channels
        android.expiry = expiry
        android.device_types = urbanairship.device_types('android')
        android.notification = payload['android']
        self.push(android)

        # Send ios notification.
        ios = urbanairship.Airship(
            self.ios_application_key,
            self.ios_master_secret
        ).create_push()
        ios.audience = audience_channels
        ios.expiry = expiry
        ios.device_types = urbanairship.device_types('ios')
        ios.notification = payload['ios']
        self.push(ios)

    def push(self, push):
        log.debug('Sending Push to Urban Airship: %s', push.payload)
        try:
            push.send()
        except urbanairship.common.Unauthorized:
            log.error(
                'Semantic error during push to Urban Airship with payload %s',
                push.payload, exc_info=True)
            raise zeit.push.interfaces.WebServiceError('Unauthorized')
        except urbanairship.common.AirshipFailure, e:
            log.error(
                'Technical error during push to Urban Airship with payload %s',
                push.payload, exc_info=True)
            raise zeit.push.interfaces.TechnicalError(str(e))

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

        tracking = collections.OrderedDict(sorted(
            {
                'wt_zmc': 'fix.int.zonaudev.push.{channel}.zeitde.{'
                          'device}.link.x'.format(channel=channel,
                                                  device=device),
                'utm_medium': 'fix',
                'utm_source': 'push_zonaudev_int',
                'utm_campaign': channel,
                'utm_content': 'zeitde_{device}_link_x'.format(device=device),
            }.items())
        )
        parts = list(urlparse.urlparse(url))
        query = collections.OrderedDict(urlparse.parse_qs(parts[4]))
        for key, value in tracking.items():
            query[key] = value
        parts[4] = urllib.urlencode(query, doseq=True)
        return urlparse.urlunparse(parts)


class Message(zeit.push.message.Message):

    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    # BBB This used to send to both parse and urbanairship, so we use
    # a generic name in the message_config.
    # TODO What is the point of this?
    grok.name('mobile')
    type = 'urbanairship'

    @property
    def log_message_details(self):
        notifier = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name=self.type)
        channels = notifier.get_channel_list(self.config.get('channels'))
        return 'Channels %s' % ' '.join(channels)

    @zope.cachedescriptors.property.Lazy
    def text(self):
        return self.config.get('override_text', self.context.title)

    @zope.cachedescriptors.property.Lazy
    def additional_parameters(self):
        result = {
            'mobile_title': self.config.get('title'),
        }
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


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(
        android_application_key=config['urbanairship-android-application-key'],
        android_master_secret=config['urbanairship-android-master-secret'],
        ios_application_key=config['urbanairship-ios-application-key'],
        ios_master_secret=config['urbanairship-ios-master-secret'],
        expire_interval=int(config['urbanairship-expire-interval']))


class PayloadDocumentation(Connection):

    def push(self, data):
        print json.dumps(data.payload, indent=2, sort_keys=True) + ','


def print_payload_documentation():
    zope.app.appsetup.product.setProductConfiguration('zeit.push', {
        CONFIG_CHANNEL_BREAKING: 'Eilmeldung',
        CONFIG_CHANNEL_NEWS: 'News',
        'push-target-url': 'http://www.zeit.de',
        'urbanairship-audience-group': 'subscriptions'
    })
    conn = PayloadDocumentation(
        'android_application_key', 'android_master_secret',
        'ios_application_key', 'ios_master_secret', expire_interval=9000)
    params = {}
    print '[{"//": "*** Eilmeldung ***"},'
    conn.send('PushTitle', 'http://www.zeit.de/test/artikel',
              channels=CONFIG_CHANNEL_BREAKING, **params)
    print '\n'
    print '{"//": "*** Wichtige Nachrichten ***"},'
    conn.send('PushTitle', 'http://www.zeit.de/test/artikel',
              channels=CONFIG_CHANNEL_NEWS, **params)
    print ']'
