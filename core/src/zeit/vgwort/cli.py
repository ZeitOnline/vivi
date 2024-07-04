"""
One way to create the required inputfile (ZON-5837):

cat articles_without_vgwort_payload.js | \
    http https://tms-es.zon.zeit.de/zeit_pool_content/_search | \
        jq -r '@text "http://xml.zeit.de" + .hits.hits[]._source.url' \
            > vgwort-nachzuegler-production
"""
import argparse
import logging
import time

import pendulum
import zope.component

import zeit.cms.interfaces
import zeit.vgwort.report


log = logging.getLogger(__name__)


def in_maintenance_hours():
    now = pendulum.now()
    today = pendulum.datetime(now.year, now.month, now.day)
    four = today.replace(hour=3, minute=50)
    six = today.replace(hour=6, minute=10)
    return four <= now <= six


# No transaction commit, as we don't care about the cache.
@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.vgwort', 'token-principal'))
def bulk_report():
    parser = argparse.ArgumentParser(description='VG Wort bulk report')
    parser.add_argument('--filename', help='filename with uniqueId per line')
    options = parser.parse_args()
    if not options.filename:
        parser.print_help()
        raise SystemExit(1)

    vgwort = zope.component.getUtility(zeit.vgwort.interfaces.IMessageService)
    for i, line in enumerate(open(options.filename)):
        # Safetybelt if the script runs veeery long
        while in_maintenance_hours():
            log.info('API maintenance, sleep 10 minutes')
            time.sleep(600)

        id = line.strip()
        try:
            content = zeit.cms.interfaces.ICMSContent(id)
            zeit.vgwort.report.report(content)
            # XXX vgwort returns 401 after some requests for unknown reasons.
            if i % 6 == 0 and hasattr(vgwort, 'client'):
                del vgwort.client
        except Exception as e:
            try:
                if e.args[0][0] == 401:
                    raise
            except IndexError:
                pass
            log.error('Error %s, skipped', id, exc_info=True)
