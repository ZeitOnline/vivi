import argparse
import logging

import zope.component

import zeit.cms.cli
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.retresco.interfaces


log = logging.getLogger(__name__)


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def delete_content():
    parser = argparse.ArgumentParser(description='Delete content')
    parser.add_argument('--filename', help='filename with uniqueId per line')
    options = parser.parse_args()
    if not options.filename:
        parser.print_help()
        raise SystemExit(1)

    for line in open(options.filename):
        id = line.strip()
        content = zeit.cms.interfaces.ICMSContent(id, None)
        if content is None:
            log.warn('Skipping %s, not found', id)
            continue

        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        if info.published:
            log.info('Skipping %s, still published', id)
            continue

        try:
            folder = content.__parent__
        except Exception:
            log.warn('Skipping %s, parent not found', id)
            continue

        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        tms.delete_id(zeit.cms.content.interfaces.IUUID(content).id)

        for _ in zeit.cms.cli.commit_with_retry(attempts=3):
            log.info('Deleting %s', id)
            del folder[content.__name__]
