from zeit.cms.application import CONFIG_CACHE
import gocept.lxml.objectify
import itertools
import json
import logging
import urllib2
import zeit.cms.tagging.interfaces
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


class GoogleNewsTopics(object):

    zope.interface.implements(zeit.cms.tagging.interfaces.ICurrentTopics)

    def __call__(self, ressort=None):
        if ressort is None:
            return list(itertools.chain(*self.keywords.values()))
        categories = self.categories.get(ressort)
        if not categories:
            result = self.keywords.get(ressort, [])
        else:
            result = list(itertools.chain(*[
                self.keywords.get(x, []) for x in categories]))
        return sorted(result, key=lambda x: (x.lower(), x))

    @property
    def keywords(self):
        self._load()
        return self._keywords

    @property
    def headlines(self):
        self._load()
        return self._headlines

    @property
    def categories(self):
        self._load()
        return self._categories

    @CONFIG_CACHE.cache_on_arguments()
    def _load(self):
        self._load_ressort_mapping()
        self._load_keywords()

    def _load_ressort_mapping(self):
        url = self._config['trisolute-ressort-url']
        log.debug('Retrieving %s', url)
        response = urllib2.urlopen(url)
        root = gocept.lxml.objectify.fromfile(response)
        mapping = {}
        for ressort in root.ressort:
            categories = mapping.setdefault(ressort.get('name'), [])
            for category in ressort.category:
                categories.append(category.text)
        self._categories = mapping

    def _load_keywords(self):
        url = self._config['trisolute-url']
        log.debug('Retrieving %s', url)
        try:
            response = urllib2.urlopen(url, timeout=10)
            data = json.loads(response.read())
        except:
            log.warning('Request to %s failed', url, exc_info=True)
            data = []
        keywords = {}
        headlines = []
        for category in data:
            if category['headlineCategory'] == 'Schlagzeilen':
                headlines = category['topics']
            else:
                keywords[category['headlineCategory']] = category['topics']
        self._keywords = keywords
        self._headlines = headlines

    @property
    def _config(self):
        return zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
