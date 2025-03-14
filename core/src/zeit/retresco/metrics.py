import argparse
import logging

from sqlalchemy import select
from sqlalchemy import text as sql
import prometheus_client
import zope.component

from zeit.cms.interfaces import ICMSContent
from zeit.connector.models import Content as ConnectorModel
from zeit.content.article.interfaces import IArticle
import zeit.cms.cli
import zeit.cms.config
import zeit.find.interfaces
import zeit.push.interfaces
import zeit.retresco.interfaces


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


def elastic(kind):
    if kind == 'external':
        return zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
    elif kind == 'internal':
        return zope.component.getUtility(zeit.find.interfaces.ICMSSearch)


def _collect_importers():
    metric = Gauge('vivi_recent_content_published_total', labelnames=['content'])
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
        metric.labels(environment(), name).set(elastic('external').search(query, rows=0).hits)


def _collect_vgwort_report():
    metric = Gauge('vivi_recent_vgwort_reported_total')
    sql_query = (
        "type = 'article' AND published = true AND vgwort_reported_on > NOW() - INTERVAL '1 hour'"
    )
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    query = select(ConnectorModel)
    query = query.where(sql(sql_query))
    metric.labels(environment()).set(connector.search_sql_counts(query))


def _collect_vgwort_token_count():
    metric = Gauge('vivi_available_vgwort_tokens_total')
    tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
    metric.labels(environment()).set(len(tokens))


def _collect_missing_tms_authors():
    metric = Counter('vivi_articles_with_missing_tms_authors')
    query = {
        'query': {
            'bool': {
                'filter': [
                    {'term': {'doc_type': 'article'}},
                    {'range': {'payload.document.date_first_released': {'gt': 'now-30m'}}},
                ]
            }
        },
        '_source': ['url', 'payload.head.authors'],
    }
    for row in elastic('external').search(query, rows=100):
        content = ICMSContent('http://xml.zeit.de' + row['url'], None)
        if not IArticle.providedBy(content):
            log.info('Skip %s, not found', row['url'])
            continue
        tms = row.get('payload', {}).get('head', {}).get('authors', [])
        for ref in content.authorships:
            id = ref.target_unique_id
            if id and id not in tms:
                log.warning('%s: author %s not found in TMS', content, id)
                metric.labels(environment()).inc()


def _collect_highest_kpi_value():
    KPI_FIELDS = zeit.retresco.interfaces.KPIFieldSource()

    def query(kpi):
        return {
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'doc_type': 'article'}},
                        {'range': {'payload.document.date_first_released': {'gt': 'now-1d'}}},
                    ]
                }
            },
            '_source': list(KPI_FIELDS.values()),
            'sort': [{kpi: 'desc'}],
        }

    metric = Gauge(
        'tms_highest_kpi_value',
        labelnames=['field'],
    )

    for name, tms in KPI_FIELDS.items():
        result = elastic('external').search(query(tms), rows=1)
        try:
            row = result[0]
        except IndexError:
            pass
        else:
            metric.labels(environment(), name).set(row.get(tms, 0))


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
