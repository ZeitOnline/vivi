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

    def get_ranking(self, service, facet=None, **kw):
        location = '.'.join(filter(bool, (service, facet)))
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
        zope.interface.alsoProvides(
            content, zeit.reach.interfaces.IReachContent)
        return content

    def _get_metadata(self, path):
        es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
        return es.search(
            {'query': {'term': {'url': path}}}, rows=1, include_payload=True)


@zope.interface.implementer(zeit.reach.interfaces.IReach)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.reach')
    return Reach(config['url'], config['freeze-now'] or None)


@grok.implementer(zeit.reach.interfaces.IKPI)
class KPI(grok.Adapter):

    grok.context(zeit.reach.interfaces.IReachContent)
    grok.provides(zeit.cms.content.interfaces.IKPI)

    def __init__(self, context):
        super().__init__(context)
        self.score = self.context._reach_data.get('score', 0)
        for name in list(zeit.cms.content.interfaces.IKPI):
            setattr(self, name, 0)
