import argparse
import gocept.runner
import grokcore.component as grok
import logging
import time
import zeit.cms.celery
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
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
    log.info('AfterAdd: Creating async index job for %s' % context.uniqueId)
    index_async.delay(context.uniqueId)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def index_after_checkin(context, event):
    if event.publishing:
        return
    index_async.apply_async((context.uniqueId,), countdown=5)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.IObjectRemovedEvent)
def unindex_on_remove(context, event):
    if zeit.cms.workingcopy.interfaces.IWorkingcopy.providedBy(
            event.oldParent):
        return
    unindex_async.delay(zeit.cms.content.interfaces.IUUID(context).id)


@zeit.cms.celery.task(queuename='search')
def index_async(uniqueId):
    context = zeit.cms.interfaces.ICMSContent(uniqueId, None)
    if context is None:
        log.warning('Could not index %s because it does not exist any longer.',
                    uniqueId)
    else:
        conf = zope.app.appsetup.appsetup.getConfigContext()
        index(
            context, enrich=True,
            update_keywords=conf.hasFeature('zeit.retresco.index_on_checkin'))


def index(content, enrich=False, update_keywords=False, publish=False):
    if update_keywords and not enrich:
        raise ValueError('enrich is required for update_keywords')
    conn = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    stack = [content]
    while stack:
        content = stack.pop(0)
        if zeit.cms.repository.interfaces.ICollection.providedBy(content):
            stack.extend(content.values())
        uuid = getattr(zeit.cms.content.interfaces.IUUID(content, None), 'id',
                       '<no-uuid>')
        log.info('Updating: %s %s, enrich: %s, keywords: %s, publish: %s',
                 content.uniqueId, uuid, enrich, update_keywords, publish)
        try:
            if enrich:
                log.debug('Enriching: %s', content.uniqueId)
                response = conn.enrich(content)
                body = response.get('body')
                if update_keywords:
                    tagger = zeit.retresco.tagger.Tagger(content)
                    tagger.update(conn.generate_keyword_list(response))
            else:
                # For reindex-only, preserve the previously enriched body.
                # Note: This only works when content is already published in
                # TMS, but for a large-scale reindex where we don't want to
                # have to enrich again that's probably fine.
                body = conn.get_article_data(content).get('body')

            conn.index(content, body)

            if publish:
                pub_info = zeit.cms.workflow.interfaces.IPublishInfo(content)
                if pub_info.published:
                    if zeit.retresco.interfaces.ITMSRepresentation(
                            content)() is not None:
                        log.info('Publishing: %s', content.uniqueId)
                        conn.publish(content)
                    else:
                        log.info(
                            'Skip publish for %s, missing required fields',
                            content.uniqueId)
        except Exception:
            log.warning('Error indexing %s', content.uniqueId, exc_info=True)
            continue


@zeit.cms.celery.task(queuename='search')
def unindex_async(uuid):
    conn = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    conn.delete_id(uuid)


@zeit.cms.celery.task(queuename='manual')
def index_parallel(unique_id, enrich=False, publish=False):
    content = zeit.cms.interfaces.ICMSContent(unique_id)

    if zeit.cms.repository.interfaces.ICollection.providedBy(content):
        children = content.values()
    else:
        children = [content]

    for item in children:
        log.debug('Looking at %s', item.uniqueId)
        if (zeit.content.image.interfaces.IImageGroup.providedBy(item) or
                zeit.content.image.interfaces.IImage.providedBy(item)):
            log.debug(
                'Skip indexing %s, it is an image/group', item.uniqueId)
            continue
        if zeit.cms.repository.interfaces.ICollection.providedBy(item):
            index_parallel.delay(item.uniqueId, enrich=enrich, publish=publish)
        else:
            start = time.time()
            index(item, enrich=enrich, update_keywords=enrich, publish=publish)
            stop = time.time()
            log.info('Processed %s in %s', item.uniqueId, stop - start)


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.retresco', 'index-principal'))
def reindex():
    parser = argparse.ArgumentParser(description='Reindex folder in TMS')
    parser.add_argument(
        'ids', type=unicode, nargs='+', help='uniqueIds to reindex')
    parser.add_argument(
        '--file', action='store_true',
        help='Load uniqueIds from a file to reindex')
    parser.add_argument(
        '--parallel', action='store_true',
        help='process via job queue instead of directly')
    parser.add_argument(
        '--enrich', action='store_true',
        help='Perform TMS analyze/enrich prior to indexing')
    parser.add_argument(
        '--publish', action='store_true',
        help='Perform TMS publish after indexing')

    args = parser.parse_args()
    ids = args.ids
    if args.file:
        if len(args.ids) > 1:
            raise Exception("Only one file can be passed!")
        with open(args.ids[0], 'r') as f:
            ids = f.read().splitlines()

    for id in ids:
        if args.parallel:
            index_parallel.delay(id, args.enrich, args.publish)
        else:
            index(
                zeit.cms.interfaces.ICMSContent(id),
                enrich=args.enrich, update_keywords=args.enrich,
                publish=args.publish)
