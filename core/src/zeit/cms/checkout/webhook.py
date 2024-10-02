import logging

import grokcore.component as grok
import requests
import transaction
import zope.lifecycleevent

from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.interfaces import CONFIG_CACHE, ITypeDeclaration
from zeit.cms.repository.interfaces import IAutomaticallyRenameable
import zeit.cms.celery
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces


log = logging.getLogger(__name__)


def create_webhook_jobs(id, context, **kwargs):
    hooks = HOOKS.factory.find(id)
    if not hooks:
        log.warning('No %s webhooks found for %s', id, context.uniqueId)
        return
    for url in hooks:
        log.info(
            f'After{id.capitalize()}: Creating async webhook jobs with'
            f' url {url} for {context.uniqueId}',
        )
        notify_webhook.apply_async((context.uniqueId, id, url), **kwargs)


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def notify_after_checkin(context, event):
    # XXX Work around redis/ZODB race condition, see BUG-796.
    if event.publishing:
        return
    create_webhook_jobs('checkin', context, countdown=5)


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.workflow.interfaces.IPublishedEvent)
def notify_after_publish(context, event):
    create_webhook_jobs('publish', context, countdown=5)


@grok.subscribe(zope.lifecycleevent.IObjectAddedEvent)
def notify_after_add(event):
    context = event.object
    if not zeit.cms.interfaces.ICMSContent.providedBy(context):
        return
    if zeit.cms.repository.interfaces.IRepository.providedBy(context):
        return
    if zeit.cms.workingcopy.interfaces.IWorkingcopy.providedBy(event.newParent):
        return
    create_webhook_jobs('add', context)


@zeit.cms.celery.task(bind=True, queue='webhook')
def notify_webhook(self, uniqueId, id, url):
    content = zeit.cms.interfaces.ICMSContent(uniqueId, None)
    if content is None:
        log.warning('Could not resolve %s, ignoring.', uniqueId)
        return
    hooks = HOOKS.factory.find(id)
    if hooks is None:
        log.warning('Hook configuration for %s has vanished, ignoring.', id)
        return
    try:
        hooks[url](content)
    except TechnicalError as e:
        raise self.retry(countdown=e.countdown)
    # Don't even think about trying to write to DAV cache, to avoid conflicts.
    transaction.abort()


class Hook:
    def __init__(self, id, url):
        self.id = id
        self.url = url
        self.excludes = []
        self.includes = []

    def __call__(self, content):
        if not self.matches_criteria(content):
            return
        log.info('Notifying %s about %s', self.url, content)
        try:
            self.deliver(content)
        except requests.exceptions.HTTPError as err:
            if getattr(err.response, 'status_code', 500) < 500:
                raise
            log.warning('Webhook %s returned error, retrying', self.url, exc_info=True)
            raise TechnicalError()
        except requests.exceptions.RequestException:
            log.warning('Webhook %s returned error, retrying', self.url, exc_info=True)
            raise TechnicalError()

    def deliver(self, content):
        r = requests.post(self.url, json=[content.uniqueId], timeout=10)
        r.raise_for_status()

    def add_exclude(self, key, value):
        self.excludes.append((key, value))

    def add_include(self, key, value):
        self.includes.append((key, value))

    def matches_criteria(self, content):
        return self.should_include(content) and not self.should_exclude(content)

    def should_include(self, content):
        if not self.includes:
            return True
        for include in self.includes:
            if self._matches(include, content):
                return True
        return False

    def should_exclude(self, content):
        renameable = getattr(IAutomaticallyRenameable(content, None), 'renameable', False)
        if renameable:
            return True
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
        typ = getattr(ITypeDeclaration(content, None), 'type_identifier', 'unknown')
        return typ == value

    def _match_product(self, content, value):
        if not ICommonMetadata.providedBy(content):
            return False
        return content.product and content.product.id == value

    def _match_product_counter(self, content, value):
        if not ICommonMetadata.providedBy(content):
            return False
        if not content.product:
            return False
        return content.product and content.product.counter == value

    def _match_path_prefix(self, content, value):
        path = content.uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE, '/')
        return path.startswith(value)


class HookSource(zeit.cms.content.sources.SimpleXMLSource):
    config_url = 'checkin-webhook-config'
    default_filename = 'checkin-webhooks.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = {}
        tree = self._get_tree()
        for node in tree.iterchildren('webhook'):
            hook = Hook(node.get('id'), node.get('url'))
            for include in node.xpath('include/*'):
                hook.add_include(include.tag, include.text)
            for exclude in node.xpath('exclude/*'):
                hook.add_exclude(exclude.tag, exclude.text)
            if not result.get(hook.id):
                result[hook.id] = {}
            result[hook.id][hook.url] = hook
        return result

    def getValues(self):
        return self._values().values()

    def find(self, id):
        return self._values().get(id)


HOOKS = HookSource()


class TechnicalError(Exception):
    def __init__(self, countdown=60):
        self.countdown = countdown
