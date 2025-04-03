import argparse
import logging

from sqlalchemy import select
from sqlalchemy import text as sql
import prometheus_client
import zope.component

from zeit.cms.content.source import FEATURE_TOGGLES
from zeit.connector.models import Content
import zeit.cms.cli
import zeit.cms.config
import zeit.connector.interfaces
import zeit.retresco.interfaces
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
    if not FEATURE_TOGGLES.find('column_read_wcm_695'):
        return
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


def _collect_bbb_importers_elastic():
    if FEATURE_TOGGLES.find('column_read_wcm_695'):
        return

    metric = Gauge('vivi_recent_content_published_total', labelnames=['content'])
    elastic = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    queries = {
        'podcast': [
            {'term': {'doc_type': 'audio'}},
            {'term': {'payload.audio.audio_type': 'podcast'}},
        ],
        'news': [{'term': {'payload.workflow.product-id': 'News'}}],
        'video': [{'term': {'doc_type': 'video'}}],
    }
    for name, query in queries.items():
        query = {
            'query': {
                'bool': {
                    'filter': [
                        {'range': {'payload.workflow.date_last_published': {'gt': 'now-1h'}}}
                    ]
                    + query
                }
            }
        }
        metric.labels(environment(), name).set(elastic.search(query, rows=0).hits)


def _collect_vgwort_report():
    metric = Gauge('vivi_recent_vgwort_reported_total')
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    query = """type = 'article' AND published = true
    AND vgwort_reported_on > NOW() - INTERVAL '1 hour'"""
    query = select(Content).where(sql(query))
    metric.labels(environment()).set(connector.search_sql_count(query))


def _collect_vgwort_token_count():
    metric = Gauge('vivi_available_vgwort_tokens_total')
    tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
    metric.labels(environment()).set(len(tokens))


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
