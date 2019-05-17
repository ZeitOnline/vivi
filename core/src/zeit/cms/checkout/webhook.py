from zeit.cms.application import CONFIG_CACHE
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.interfaces import ITypeDeclaration
import grokcore.component as grok
import logging
import requests
import zeit.cms.celery
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zope.lifecycleevent


log = logging.getLogger(__name__)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def notify_after_checkin(context, event):
    if event.publishing:
        return
    # XXX Work around redis/ZODB race condition, see BUG-796.
    notify_webhooks.apply_async((context.uniqueId,), countdown=5)


@grok.subscribe(zope.lifecycleevent.IObjectAddedEvent)
def notify_after_add(event):
    context = event.object
    if not zeit.cms.interfaces.ICMSContent.providedBy(context):
        return
    if zeit.cms.repository.interfaces.IRepository.providedBy(context):
        return
    if zeit.cms.workingcopy.interfaces.IWorkingcopy.providedBy(
            event.newParent):
        return
    notify_webhooks.delay(context.uniqueId)


@zeit.cms.celery.task(queuename='webhook')
def notify_webhooks(uniqueId):
    content = zeit.cms.interfaces.ICMSContent(uniqueId, None)
    if content is None:
        log.warning('Could not resolve %s, ignoring.', uniqueId)
        return
    for hook in HOOKS:
        hook(content)


class Hook(object):

    def __init__(self, url):
        self.url = url
        self.excludes = []

    def __call__(self, content):
        if self.should_exclude(content):
            return
        log.debug('Notifying %s about %s', self.url, content)
        self.deliver(content)

    def deliver(self, content):
        requests.post(self.url, json=[content.uniqueId])

    def add_exclude(self, key, value):
        self.excludes.append((key, value))

    def should_exclude(self, content):
        for exclude in self.excludes:
            if self._matches(exclude, content):
                log.debug('Skipping %s, matched exclude %s', content, exclude)
                return True
        return False

    def _matches(self, exclude, content):
        key, value = exclude
        func = getattr(self, '_match_%s' % key)
        return func(content, value)

    def _match_type(self, content, value):
        typ = getattr(
            ITypeDeclaration(content, None), 'type_identifier', 'unknown')
        return typ == value

    def _match_product(self, content, value):
        if not ICommonMetadata.providedBy(content):
            return False
        return content.product and content.product.id == value


class HookSource(zeit.cms.content.sources.SimpleXMLSource):

    config_url = 'checkin-webhook-config'

    @CONFIG_CACHE.cache_on_arguments()
    def getValues(self):
        result = []
        tree = self._get_tree()
        for node in tree.iterchildren('webhook'):
            hook = Hook(node.get('url'))
            for exclude in node.xpath('exclude/*'):
                hook.add_exclude(exclude.tag, exclude.text)
            result.append(hook)
        return result


HOOKS = HookSource()
