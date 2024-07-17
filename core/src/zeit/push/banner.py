import logging

import grokcore.component as grok
import lxml.builder
import zope.interface

from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import ICheckinManager
from zeit.cms.workflow.interfaces import PRIORITY_HOMEPAGE, IPublish
import zeit.cms.config
import zeit.push.interfaces
import zeit.push.message


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.push.interfaces.IBanner)
class Banner:
    def __init__(self, banner_unique_id):
        self.banner_unique_id = banner_unique_id

    @property
    def article_id(self):
        if self.xml_banner is None:
            return None
        article = self.xml_banner.xml.find('article_id')
        if article is None:
            return None
        return article.text

    @article_id.setter
    def article_id(self, value):
        self._ensure_unlocked()
        with checked_out(self.xml_banner) as co:
            node = co.xml.find('article_id')
            if node is None:
                co.xml.append(lxml.builder.E.article_id(value or ''))
            else:
                node.text = value

    @property
    def xml_banner(self):
        content = zeit.cms.interfaces.ICMSContent(self.banner_unique_id, None)
        if not zeit.cms.content.interfaces.IXMLContent.providedBy(content):
            return None
        return content

    def publish(self):
        IPublish(self.xml_banner).publish(background=False, priority=PRIORITY_HOMEPAGE)

    def _ensure_unlocked(self):
        banner = zeit.cms.interfaces.ICMSContent(self.banner_unique_id)
        lockable = zope.app.locking.interfaces.ILockable(banner, None)
        if not lockable:
            return
        if lockable.isLockedOut():
            lockable.breaklock()
        if lockable.ownLock():
            checked_out = zeit.cms.interfaces.ICMSWCContent(banner.uniqueId, None)
            if checked_out is not None:
                ICheckinManager(checked_out).delete()


@zope.interface.implementer(zeit.push.interfaces.IBanner)
def homepage_banner():
    return Banner(zeit.cms.config.required('zeit.push', 'homepage-banner-uniqueid'))


def get_breaking_news_article():
    banner = zope.component.getUtility(zeit.push.interfaces.IBanner)
    return zeit.cms.interfaces.ICMSContent(banner.article_id, None)


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
class Push:
    def send(self, text, article_unique_id, **kw):
        log.debug('Publishing Homepage banner for %s', article_unique_id)
        banner = zope.component.getUtility(zeit.push.interfaces.IBanner)
        banner.article_id = article_unique_id
        banner.publish()


class HomepageMessage(zeit.push.message.Message):
    grok.name('homepage')
    get_text_from = 'short_text'

    @property
    def url(self):
        # zeit.web expects a uniqueId and then renders the link itself.
        return self.context.uniqueId
