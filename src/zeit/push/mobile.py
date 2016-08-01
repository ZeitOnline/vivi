from zeit.push.interfaces import PARSE_NEWS_CHANNEL
import grokcore.component as grok
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.image.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zeit.cms.content.interfaces
import zeit.cms.checkout.interfaces
import zeit.push.interfaces


class Message(zeit.push.message.Message):

    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('mobile')

    def send_push_notification(self, **kw):
        for mobile_service in ['parse', 'urbanairship']:
            notifier = zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name=mobile_service)
            notifier.send(self.text, self.url, **kw)

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
                zeit.cms.interfaces.ID_NAMESPACE, 'http://images.zeit.de/')
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
        config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
        return config['parse-image-pattern']


class ParseMessage(Message):
    """BW compat"""

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
