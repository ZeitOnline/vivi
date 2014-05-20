from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.content.article.edit.interfaces import IBreakingNewsBody
import grokcore.component as grok
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.interface


class StaticArticlePublisher(object):

    zope.interface.implements(zeit.push.interfaces.IPushNotifier)

    def __init__(self, uniqueId):
        self.uniqueId = uniqueId

    def send(self, text, link, **kw):
        article = ICMSContent(self.uniqueId)
        with checked_out(article, semantic_change=True) as co:
            IBreakingNewsBody(co).text = '<a href="{link}">{text}</a>'.format(
                link=link, text=text)
        IPublishInfo(article).urgent = True
        IPublish(article).publish()


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.push')
    return StaticArticlePublisher(config['eilmeldung-uniqueid'])


class Message(zeit.push.message.Message):

    grok.name('homepage')
    get_text_from = 'short_text'
