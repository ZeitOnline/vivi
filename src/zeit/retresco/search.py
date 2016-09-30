import elasticsearch
import json
import zeit.cms.interfaces
import zeit.retresco.interfaces
import zope.interface


class Elasticsearch(object):
    """Search via Elasticsearch."""

    zope.interface.implements(zeit.retresco.interfaces.IElasticsearch)

    def __init__(self, url, index):
        self.client = elasticsearch.Elasticsearch([url])
        self.index = index

    def search(
            self, query, sort_order, start=0, rows=25, include_payload=False):
        """Search using `query` and sort by `sort_order`."""
        query = query.copy()
        query['_source'] = ['url', 'doc_type', 'doc_id']
        if include_payload:
            query['_source'].append('payload')
        __traceback_info__ = (self.index, query)
        response = self.client.search(
            index=self.index, body=json.dumps(query),
            sort=sort_order, from_=start, size=rows, doc_type='documents')
        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            result = {'uniqueId': self._path_to_url(source['url']),
                      'doc_id': source['doc_id'],
                      'doc_type': source['doc_type']}
            if include_payload:
                result.update(source['payload'])
                result['keywords'] = []
                for entity_type in zeit.retresco.interfaces.ENTITY_TYPES:
                    for tag in source.get('rtr_{}s'.format(entity_type), ()):
                        result['keywords'].append(zeit.retresco.tag.Tag(
                            label=tag, entity_type=entity_type))

            results.append(result)
        search_result = zeit.cms.interfaces.Result(results)
        search_result.hits = response['hits']['total']
        return search_result

    def _path_to_url(self, path):
        return path.replace('/', zeit.cms.interfaces.ID_NAMESPACE, 1)


@zope.interface.implementer(zeit.retresco.interfaces.IElasticsearch)
def from_product_config():
    """Get the utility configured with data from the product config."""
    config = zope.app.appsetup.product.getProductConfiguration('zeit.retresco')
    return Elasticsearch(config['elasticsearch-url'],
                         config['elasticsearch-index'])
