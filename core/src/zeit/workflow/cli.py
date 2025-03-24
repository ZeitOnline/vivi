import logging

import z3c.celery.celery
import zope.component

from zeit.cms.cli import commit_with_retry, runner
import zeit.cms.workflow.interfaces


log = logging.getLogger(__name__)


@runner(principal=zeit.cms.cli.from_config('zeit.workflow', 'retract-timebased-principal'))
def retract_overdue_objects():
    import zeit.find.interfaces
    import zeit.retresco.interfaces

    tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    es = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
    unretracted = es.search(
        {
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'payload.workflow.published': True}},
                        {'range': {'payload.workflow.released_to': {'lt': 'now-15m'}}},
                    ]
                }
            },
            '_source': ['url', 'doc_id'],
        },
        rows=1000,
    )

    for item in unretracted:
        uniqueId = 'http://xml.zeit.de' + item['url']
        content = zeit.cms.interfaces.ICMSContent(uniqueId, None)
        if content is None:
            log.info('Not found: %s, deleting from TMS', uniqueId)
            tms.delete_id(item['doc_id'])
        else:
            publish = zeit.cms.workflow.interfaces.IPublish(content)
            for _ in commit_with_retry():
                log.info('Retracting %s', content)
                try:
                    publish.retract(background=False)
                except z3c.celery.celery.HandleAfterAbort as e:
                    if 'LockingError' in e.message:  # kludgy
                        log.warning('Skip %s due to %s', content, e.message)
                        break
                    raise
