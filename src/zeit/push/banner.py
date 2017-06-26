from datetime import datetime
from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import ICheckinManager
from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.content.article.edit.interfaces import IBreakingNewsBody
import grokcore.component as grok
import logging
import pytz
import transaction
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
        self._ensure_unlocked(article)
        with checked_out(article) as co:
            IBreakingNewsBody(co).text = u'<a href="{link}">{text}</a>'.format(
                link=link, text=text)
            # XXX The checked_out helper is rather technical (it does not
            # simulate a complete user interaction), thus specifying
            # checked_out(semantic_change=True) doesn't help: Since the checked
            # out object is newly created and we don't (can't?) call
            # transaction.commit() here (and a temporary workingcopy does not
            # really participate in the ZODB machinery anyway), the _p_mtime of
            # the checked out object is not set, which means its modified date
            # is not updated -- which means LSC would be set to the last
            # modified date taken from the repository, which is not what we
            # want.
            ISemanticChange(co).last_semantic_change = datetime.now(pytz.UTC)
        IPublishInfo(article).urgent = True
        IPublish(article).publish()

    def _ensure_unlocked(self, content):
        lockable = zope.app.locking.interfaces.ILockable(content, None)
        if not lockable:
            return
        if lockable.isLockedOut():
            lockable.breaklock()
        if lockable.ownLock():
            checked_out = zeit.cms.interfaces.ICMSWCContent(
                content.uniqueId, None)
            if checked_out is not None:
                ICheckinManager(checked_out).delete()


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def homepage_banner():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return StaticArticlePublisher(config['homepage-banner-uniqueid'])


class HomepageMessage(zeit.push.message.Message):

    grok.name('homepage')
    get_text_from = 'short_text'

    def _disable_message_config(self):
        transaction.get().addAfterCommitHook(
            self._disable_message_config_on_commit)

    def _disable_message_config_on_commit(self, commit_success):
        if commit_success:
            super(HomepageMessage, self)._disable_message_config()

    @property
    def url(self):
        # zeit.web expects a uniqueId and then renders the link itself.
        return self.context.uniqueId
