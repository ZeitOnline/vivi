import elasticsearch
import json
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zeit.retresco.interfaces
import zope.interface


@zope.interface.implementer(zeit.retresco.interfaces.IElasticsearch)
class Elasticsearch(object):
    """Search via Elasticsearch."""

    def __init__(self, url):
        self.client = elasticsearch.Elasticsearch([url])

    def search(self, query, sort_order, start=0, rows=25):
        """Search using `query` and sort by `sort_order`."""
        query = query.copy()
        query['_source'] = 'url'
        __traceback_info__ = query
        response = self.client.search(
            # FIXME index must be configured via product config
            # FIXME doctype = documents
            index='zeit_pool', body=json.dumps(query), sort=sort_order,
            from_=start, size=rows)
        result = zeit.cms.tagging.interfaces.Result(
            {'uniqueId': self._path_to_url(x['_source']['url'])}
            for x in response['hits']['hits'])
        result.hits = response['hits']['total']
        return result

    def _path_to_url(self, path):
        return path.replace('/', zeit.cms.interfaces.ID_NAMESPACE, 1)


@zope.interface.implementer(zeit.retresco.interfaces.IElasticsearch)
def from_product_config():
    """Get the utility configured with data from the product config."""
    config = zope.app.appsetup.product.getProductConfiguration('zeit.retresco')
    return Elasticsearch(config['elasticsearch-url'])
