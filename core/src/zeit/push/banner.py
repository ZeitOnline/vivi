from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import ICheckinManager
from zeit.cms.workflow.interfaces import IPublish, PRIORITY_HOMEPAGE
import grokcore.component as grok
import logging
import transaction
import zeit.push.interfaces
import zeit.push.message
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.push.interfaces.IBanner)
class Banner:

    def __init__(self, banner_unique_id):
        self.banner_unique_id = banner_unique_id

    @property
    def article_id(self):
        if self.xml_banner is None:
            return None
        if not self.xml_banner.xml.article_id:
            return None
        return self.xml_banner.xml.article_id.text

    @article_id.setter
    def article_id(self, value):
        self._ensure_unlocked()
        with checked_out(self.xml_banner) as co:
            co.xml.article_id = value

    @property
    def xml_banner(self):
        content = zeit.cms.interfaces.ICMSContent(self.banner_unique_id, None)
        if not zeit.cms.content.interfaces.IXMLContent.providedBy(content):
            return None
        return content

    def publish(self):
        IPublish(self.xml_banner).publish(priority=PRIORITY_HOMEPAGE)

    def retract(self):
        IPublish(self.xml_banner).retract(priority=PRIORITY_HOMEPAGE)

    def _ensure_unlocked(self):
        banner = zeit.cms.interfaces.ICMSContent(self.banner_unique_id)
        lockable = zope.app.locking.interfaces.ILockable(banner, None)
        if not lockable:
            return
        if lockable.isLockedOut():
            lockable.breaklock()
        if lockable.ownLock():
            checked_out = zeit.cms.interfaces.ICMSWCContent(
                banner.uniqueId, None)
            if checked_out is not None:
                ICheckinManager(checked_out).delete()


@zope.interface.implementer(zeit.push.interfaces.IBanner)
def homepage_banner():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Banner(config['homepage-banner-uniqueid'])


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

    def _disable_message_config(self):
        transaction.get().addAfterCommitHook(
            self._disable_message_config_on_commit)

    def _disable_message_config_on_commit(self, commit_success):
        if commit_success:
            super()._disable_message_config()
            # XXX Here be dragons. The 2PC protocol has finished successfully
            # at this point, but we're still in that same logical transaction.
            # Now we have just created new changes and need to commit them,
            # which is not really a task for commit hooks.
            #
            # transaction._callAfterCommitHooks() wisely tries to prevent
            # people doing stuff like this (by removing all 2PC participants
            # after all hooks have run), but doesn't quite succeed, which leads
            # to "Duplicate tpc_begin calls for same transaction" errors inside
            # ZEO.ClientStorage.tpc_begin; although I don't really know how or
            # why (also, this doesn't happen in tests, only actual server).
            #
            # We cheat and abuse the fact that the transaction object does not
            # care and allows itself to be commited twice, thereby starting a
            # _new_ 2PC run, which then luckily _happens_ to work out fine.
            transaction.commit()

    @property
    def url(self):
        # zeit.web expects a uniqueId and then renders the link itself.
        return self.context.uniqueId
