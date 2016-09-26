import elasticsearch
import json
import zeit.cms.interfaces
import zeit.retresco.interfaces
import zope.interface


class Elasticsearch(object):
    """Search via Elasticsearch."""

    zope.interface.implements(zeit.retresco.interfaces.IElasticsearch)

    def __init__(self, url):
        self.client = elasticsearch.Elasticsearch([url])

    def search(self, query, sort_order, start=0, rows=25):
        """Search using `query` and sort by `sort_order`."""
        query = query.copy()
        query['_source'] = 'url'
        __traceback_info__ = query
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.retresco')
        response = self.client.search(
            index=config['elasticsearch-index'], body=json.dumps(query),
            sort=sort_order, from_=start, size=rows, doc_type='documents')
        result = zeit.cms.interfaces.Result(
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
