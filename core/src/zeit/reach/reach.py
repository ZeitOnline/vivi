# -*- coding: utf-8 -*-
import grokcore.component as grok
import logging
import requests
import zeit.cms.content.interfaces
import zeit.reach.interfaces
import zeit.retresco.interfaces
import zope.component
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.reach.interfaces.IReach)
class Reach:

    http = requests.Session()
    timeout = 0.2

    def __init__(self, url, freeze_now=None):
        self.url = url
        self.freeze_now = freeze_now

    def _get(self, location, **kw):
        url = '%s/%s' % (self.url, location)
        return self.http.get(url, params=kw, timeout=self.timeout)

    def get_ranking(self, typ, facet=None, **kw):
        location = '.'.join(filter(bool, (typ, facet)))
        kw.setdefault('limit', 3)
        if self.freeze_now:
            kw['now'] = self.freeze_now

        response = self._get('/'.join(('ranking', location)), **kw)
        # XXX Ugly API so that zeit.web can override _get() to write metrics;
        # this should actually be handled by a custom requests.Session.
        docs = response.json()
        result = []
        for doc in docs:
            content = self._resolve(doc)
            if content is None:
                continue
            result.append(content)
        return result

    def _resolve(self, doc):
        try:
            result = self._get_metadata(doc['location'])
            content = zeit.retresco.interfaces.ITMSContent(result[0])
            content._reach_data = doc
        except Exception:
            log.warning('Resolving %s failed', doc, exc_info=True)
            return None
        return content

    def _get_metadata(self, path):
        es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
        return es.search(
            {'query': {'term': {'url': path}}}, rows=1, include_payload=True)


@zope.interface.implementer(zeit.reach.interfaces.IReach)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.reach')
    return Reach(config['url'], config['freeze-now'] or None)
