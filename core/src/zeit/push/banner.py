from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.content.article.edit.interfaces import IBreakingNewsBody
import grokcore.component as grok
import logging
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


class StaticArticlePublisher(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    def __init__(self, uniqueId):
        self.uniqueId = uniqueId

    def send(self, text, link, **kw):
        article = ICMSContent(self.uniqueId)
        log.debug('Setting %s, %s as body of %s', text, link, self.uniqueId)
        with checked_out(article, semantic_change=True) as co:
            IBreakingNewsBody(co).text = u'<a href="{link}">{text}</a>'.format(
                link=link, text=text)
        IPublishInfo(article).urgent = True
        IPublish(article).publish()


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def homepage_banner():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return StaticArticlePublisher(config['homepage-banner-uniqueid'])


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def ios_legacy():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return StaticArticlePublisher(config['ios-legacy-uniqueid'])


class HomepageMessage(zeit.push.message.OneTimeMessage):

    grok.name('homepage')
    get_text_from = 'short_text'


class LegacyIOSMessage(zeit.push.message.OneTimeMessage):

    grok.name('ios-legacy')
    get_text_from = 'short_text'


class Retract(object):

    @property
    def homepage(self):
        notifier = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='homepage')
        return ICMSContent(notifier.uniqueId)

    @property
    def ios_legacy(self):
        notifier = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='ios-legacy')
        return ICMSContent(notifier.uniqueId)
