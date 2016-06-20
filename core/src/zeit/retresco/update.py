import argparse
import gocept.async
import gocept.runner
import grokcore.component as grok
import logging
import zeit.cms.async
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.retresco.interfaces
import zope.component
import zope.lifecycleevent


log = logging.getLogger(__name__)


@grok.subscribe(zope.lifecycleevent.IObjectAddedEvent)
def index_after_add(event):
    # We don't use the "extended" (object, event) method, as we are not
    # interested in the events which are dispatched to sublocations.
    context = event.object
    if not zeit.cms.interfaces.ICMSContent.providedBy(context):
        return
    if zeit.cms.repository.interfaces.IRepository.providedBy(context):
        return
    if zeit.cms.workingcopy.interfaces.IWorkingcopy.providedBy(
            event.newParent):
        return
    log.info('AfterAdd: Creating async index job for %s (async=%s)' % (
        context.uniqueId, gocept.async.is_async()))
    index_async(context.uniqueId)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def index_after_checkin(context, event):
    index_async(context.uniqueId)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.IObjectRemovedEvent)
def unindex_on_remove(context, event):
    if zeit.cms.workingcopy.interfaces.IWorkingcopy.providedBy(
            event.oldParent):
        return
    unindex_async(context.uniqueId)


@zeit.cms.async.function(queue='search')
def index_async(uniqueId):
    context = zeit.cms.interfaces.ICMSContent(uniqueId, None)
    if context is None:
        log.warning('Could not index %s because it does not exist any longer.',
                    uniqueId)
    else:
        index(context)


def index(content):
    conn = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    stack = [content]
    while stack:
        content = stack.pop(0)
        if zeit.cms.repository.interfaces.ICollection.providedBy(content):
            stack.extend(content.values())
        log.info('Updating: %s', content.uniqueId)
        conn.index(content)


@zeit.cms.async.function(queue='search')
def unindex_async(uniqueId):
    conn = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    conn.delete(zeit.cms.interfaces.ICMSContent(uniqueId))


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.retresco', 'index-principal'))
def reindex():
    parser = argparse.ArgumentParser(description='Reindex folder in TMS')
    parser.add_argument(
        'ids', type=unicode, nargs='+', help='uniqueIds to reindex')

    args = parser.parse_args()
    for id in args.ids:
        index(zeit.cms.interfaces.ICMSContent(id))
