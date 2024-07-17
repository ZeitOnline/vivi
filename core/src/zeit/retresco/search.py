import importlib.metadata

import elasticsearch
import elasticsearch.connection
import elasticsearch.transport
import requests.utils
import zope.dottedname.resolve
import zope.interface

import zeit.cms.config
import zeit.cms.interfaces
import zeit.retresco.interfaces


class Connection(elasticsearch.connection.RequestsHttpConnection):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.session.headers['User-Agent'] = self._user_agent()

    def _user_agent(self):
        return requests.utils.default_user_agent(
            'zeit.retresco-%s/python-requests' % (importlib.metadata.version('vivi.core'))
        )


def TransportWithConnection(connection_class):
    def factory(*args, **kw):
        kw['connection_class'] = connection_class
        return elasticsearch.transport.Transport(*args, **kw)

    return factory


@zope.interface.implementer(zeit.retresco.interfaces.IElasticsearch)
class Elasticsearch:
    """Search via Elasticsearch."""

    def __init__(self, url, index, connection_class=Connection):
        self.client = elasticsearch.Elasticsearch(
            [url], transport_class=TransportWithConnection(connection_class)
        )
        self.index = index

    def search(self, query, start=0, rows=25, include_payload=False):
        """Search using `query`. Pagination is
        available through the `start` and `rows` parameter.

        The search results include the entire payload node (as specified by
        our schema), if the `include_playload` flag is set.

        To select specific fields, the `query` may include a `_source` node.
        Hint: A custom `_source` definition is mutually exclusive with the
        `include_payload` flag.
        """

        query = query.copy()
        if '_source' in query:
            if include_payload:
                raise ValueError(
                    'Cannot include payload with specified source: %s' % (query['_source'],)
                )
        else:
            query['_source'] = ['url', 'doc_type', 'doc_id']
            if include_payload:
                query['_source'].append('payload')

        # XXX Kludgy heuristics, should we use an explicit "elasticsearch
        # version" setting instead?
        if 'cloud.es.io' in self.client.transport.hosts[0]:
            query['track_total_hits'] = True

        __traceback_info__ = (self.index, query)
        response = self.client.search(index=self.index, from_=start, size=rows, **query)
        result = zeit.cms.interfaces.Result([x['_source'] for x in response['hits']['hits']])
        if isinstance(response['hits']['total'], int):  # BBB ES-2.x
            result.hits = response['hits']['total']
        else:
            result.hits = response['hits']['total']['value']
        return result

    def aggregate(self, query):
        """Returns aggregated data from payload aggregations. Consult Elastic
        Search - Aggregations documentation for further information."""

        __traceback_info__ = (self.index, query)
        response = self.client.search(index=self.index, **query)
        return response['aggregations']

    def date_range(self, start, end):
        return date_range(start, end)


def date_range(start, end):
    result = {}
    if start is not None:
        result['gte'] = start.isoformat()
    if end is not None:
        result['lte'] = end.isoformat()
    return result


@zope.interface.implementer(zeit.retresco.interfaces.IElasticsearch)
def from_product_config():
    """Get the utility configured with data from the product config."""
    config = zeit.cms.config.package('zeit.retresco')
    return Elasticsearch(
        config['elasticsearch-url'],
        config['elasticsearch-index'],
        zope.dottedname.resolve.resolve(config['elasticsearch-connection-class']),
    )
