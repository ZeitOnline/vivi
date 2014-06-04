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
            IBreakingNewsBody(co).text = u'<a href="{link}">{text}</a>'.format(
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


# XXX This is for the old system only, remove once VIV-25 is fully implemented.
from datetime import datetime
import pytz
import zeit.cms.workflow.interfaces
import zope.component


@grok.subscribe(ICMSContent, zeit.cms.workflow.interfaces.IPublishedEvent)
def push_to_parse_legacy_eilmeldung(context, event):
    if context.uniqueId != 'http://xml.zeit.de/eilmeldung/eilmeldung':
        return
    last_pushed = zeit.push.interfaces.IPushMessages(
        context).date_last_pushed
    last_published = zeit.cms.workflow.interfaces.IPublishInfo(
        context).date_last_published
    if (last_pushed and last_published and last_pushed >= last_published):
        return

    notifier = zope.component.getUtility(
        zeit.push.interfaces.IPushNotifier, name='parse')
    notifier.send(context.xml.body.division.p.text, 'http://www.zeit.de/',
                  title=u'Eilmeldung')
    zeit.push.interfaces.IPushMessages(
        context).date_last_pushed = datetime.now(pytz.UTC)
