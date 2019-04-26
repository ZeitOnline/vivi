import grokcore.component as grok
import requests
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zope.app.appsetup.product
import zeit.cms.celery


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def notify_after_checkin(context, event):
    if event.publishing:
        return
    # XXX Work around redis/ZODB race condition, see BUG-796.
    notify_webhooks.apply_async((context.uniqueId,), countdown=5)


@zeit.cms.celery.task(queuename='webhook')
def notify_webhooks(uniqueId):
    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    for url in config.get('checkin-webhooks', '').split(' '):
        if not url:
            continue
        requests.post(url, json=[uniqueId])
