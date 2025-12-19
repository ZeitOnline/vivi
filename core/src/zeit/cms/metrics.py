import argparse
import logging

from sqlalchemy import select
from sqlalchemy import text as sql
import prometheus_client
import zope.component

from zeit.connector.models import Content
import zeit.cms.cli
import zeit.cms.config
import zeit.connector.interfaces
import zeit.vgwort.interfaces


REGISTRY = prometheus_client.CollectorRegistry()
log = logging.getLogger(__name__)


class Metric:
    def __init__(self, name, **kw):
        labels = ['environment']
        for x in kw.pop('labelnames', ()):
            labels.append(x)
        kw.update(
            {
                'name': name,
                'documentation': '',
                'labelnames': labels,
                'registry': REGISTRY,
            }
        )
        super().__init__(**kw)


class Gauge(Metric, prometheus_client.Gauge):
    pass


class Counter(Metric, prometheus_client.Counter):
    pass


def environment():
    return zeit.cms.config.required('zeit.cms', 'environment')


def _collect_importers():
    metric = Gauge('vivi_recent_content_published_total', labelnames=['content'])
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    queries = {
        'podcast': "type='audio' AND audio_type='podcast'",
        'news': "product='News'",
        'video': "type='video'",
    }
    for name, query in queries.items():
        query += " AND published=true AND date_last_published > NOW() - interval '1 hour'"
        query = select(Content).where(sql(query))
        metric.labels(environment(), name).set(connector.search_sql_count(query))


def _collect_vgwort_report_success():
    metric = Gauge('vivi_recent_vgwort_reported_total')
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    query = """type = 'article' AND published = true
    AND vgwort_reported_on > NOW() - INTERVAL '1 hour'"""
    query = select(Content).where(sql(query))
    metric.labels(environment()).set(connector.search_sql_count(query))


def _collect_vgwort_report_missing():
    metric = Gauge('vivi_vgwort_unreported_total')
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    # Similar to the conditions used in zeit.vgwort.report to find reportable
    # content, but with an earlier time window, i.e. this should never return
    # anything because all that could match should already have been reported.
    query = """type = 'article' AND published = true
    AND vgwort_private_token IS NOT NULL
    AND vgwort_reported_on IS NULL
    AND vgwort_reported_error IS NULL
    AND date_first_released <= CURRENT_DATE - INTERVAL ':cutoff days'
    AND date_first_released >= CURRENT_DATE - INTERVAL ':age_limit days'
    """
    cutoff = int(zeit.cms.config.required('zeit.vgwort', 'days-age-limit-report'))
    query = select(Content).where(sql(query).bindparams(cutoff=cutoff, age_limit=2 * cutoff))
    metric.labels(environment()).set(connector.search_sql_count(query))


def _collect_vgwort_token_count():
    metric = Gauge('vivi_available_vgwort_tokens_total')
    tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
    metric.labels(environment()).set(len(tokens))


def _collect_content_not_retracted_count():
    """Report content that should be retracted but is still published
    The 30 minute buffer accounts for normal cron execution delays (runs every 5 min)
    """
    metric = Gauge('vivi_content_not_retracted_total')
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)

    query = """
        SELECT COUNT(DISTINCT so.content)
        FROM scheduled_operations so
        INNER JOIN properties c ON so.content = c.id
        WHERE so.operation = 'retract'
          AND so.scheduled_on <= NOW() - INTERVAL '30 minutes'
          AND so.executed_on IS NULL
          AND c.published = true
    """
    query = sql(query)

    result = connector.execute_sql(query).scalar() or 0
    metric.labels(environment()).set(result)


@zeit.cms.cli.runner()
def collect():
    """Collects all app-specific metrics that we have. Mostly these are based
    on ES queries, but not all of them. This is probably *not* the best
    factoring, but the overall amount is so little that putting in a larger
    architecture/mechanics is just not worth it at this point.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--pushgateway')
    options = parser.parse_args()

    for name, func in list(globals().items()):
        if not name.startswith('_collect'):
            continue
        func()

    if not options.pushgateway:
        print(prometheus_client.generate_latest(REGISTRY).decode('utf-8'))
    else:
        prometheus_client.push_to_gateway(options.pushgateway, job=__name__, registry=REGISTRY)
