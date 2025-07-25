import importlib.metadata

import elastic_transport
import elasticsearch
import requests.utils
import zope.dottedname.resolve
import zope.interface

from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.cms.config
import zeit.cms.interfaces
import zeit.retresco.interfaces


class Connection(elastic_transport.RequestsHttpNode):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.headers['User-Agent'] = self._user_agent()

    def _user_agent(self):
        return requests.utils.default_user_agent(
            'zeit.retresco-%s/python-requests' % (importlib.metadata.version('vivi.core'))
        )


def TransportWithConnection(connection_class):
    def factory(*args, **kw):
        kw['node_class'] = connection_class
        transport = elastic_transport.Transport(*args, **kw)
        return transport

    return factory


@zope.interface.implementer(zeit.retresco.interfaces.IElasticsearch)
class Elasticsearch:
    """Search via Elasticsearch."""

    def __init__(self, url, index, connection_class=Connection):
        self.client = elasticsearch.Elasticsearch(
            [url], transport_class=TransportWithConnection(connection_class)
        )
        # Bypass version check, we're only talking to known servers anyway.
        self.client._verified_elasticsearch = True
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
        if FEATURE_TOGGLES.find('disable_elasticsearch'):
            return zeit.cms.interfaces.Result()

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

        query['track_total_hits'] = True

        __traceback_info__ = (self.index, query)
        response = self.client.search(index=self.index, from_=start, size=rows, **query)
        result = zeit.cms.interfaces.Result([x['_source'] for x in response['hits']['hits']])
        result.hits = response['hits']['total']['value']
        return result

    def aggregate(self, query):
        """Returns aggregated data from payload aggregations. Consult Elastic
        Search - Aggregations documentation for further information."""
        if FEATURE_TOGGLES.find('disable_elasticsearch'):
            return {}

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
