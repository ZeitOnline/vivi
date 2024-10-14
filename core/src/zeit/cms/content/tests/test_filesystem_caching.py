from os import environ
from pathlib import Path
from unittest.mock import patch

from transaction import commit
from zope.component import getGlobalSiteManager, getUtility

from zeit.cms.content import caching
from zeit.cms.interfaces import ICMSContent
from zeit.cms.repository.interfaces import IRepository
from zeit.cms.testing import ZeitCmsTestCase
from zeit.connector.filesystem import Connector
from zeit.connector.interfaces import IConnector


class FilesystemCachingTest(ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        environ['CONTENT_CACHE_SIZE'] = '5'
        path = getUtility(IConnector).repository_path
        connector = Connector(path)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(connector, IConnector)
        repository = getUtility(IRepository)
        self.getcontent_patch = patch.object(
            type(repository), 'getContent', wraps=repository.getContent
        )
        self.getcontent = self.getcontent_patch.start()
        self.getproperty_patch = patch(
            'zeit.cms.content.dav.IntProperty.fromProperty',
            return_value=2024,
        )
        self.getproperty = self.getproperty_patch.start()
        self.path = Path(path)
        self.reset_cache()

    def tearDown(self):
        self.getproperty_patch.stop()
        self.getcontent_patch.stop()
        self.reset_cache()
        super().tearDown()

    def reset_cache(self):
        cache = vars(caching)['__cache']  # reset the cache by removing
        if hasattr(cache, 'cache'):  # the `cache` attribute
            delattr(cache, 'cache')

    def test_content_is_cached(self):
        assert self.getcontent.call_count == 0
        a = ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 1
        commit()  # new transaction (aka request)
        b = ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 1
        assert a is b

    def test_content_is_invalidated_by_update(self):
        a = ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 1
        commit()  # new transaction (aka request)
        self.path.joinpath('testcontent').touch()
        b = ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 2
        assert a is not b

    def test_dav_properties_are_cached(self):
        assert self.getproperty.call_count == 0
        a = ICMSContent('http://xml.zeit.de/contentwithproperty')
        a.year == 2024
        assert self.getproperty.call_count == 1
        commit()  # new transaction (aka request)
        b = ICMSContent('http://xml.zeit.de/contentwithproperty')
        assert b.year == 2024
        # assert self.getproperty.call_count == 1

    def test_dav_properties_are_invalidated_by_update(self):
        a = ICMSContent('http://xml.zeit.de/contentwithproperty')
        assert a.year == 2024
        assert self.getproperty.call_count == 1
        commit()  # new transaction (aka request)
        self.path.joinpath('contentwithproperty.meta').touch()
        b = ICMSContent('http://xml.zeit.de/contentwithproperty')
        assert b.year == 2024
        assert self.getproperty.call_count == 2

    def test_least_recently_used_content_is_removed(self):
        cache = vars(caching)['__cache'].cache
        ICMSContent('http://xml.zeit.de/2006/49/Young')
        ICMSContent('http://xml.zeit.de/2006/52/Stimmts')
        ICMSContent('http://xml.zeit.de/2007/01/Macher')
        ICMSContent('http://xml.zeit.de/2007/01/Miami')
        ICMSContent('http://xml.zeit.de/2007/02/Verfolgt')
        assert len(cache) == 5
        assert 'http://xml.zeit.de/2006/49/Young' in cache
        assert 'http://xml.zeit.de/2007/01/Miami' in cache
        assert 'http://xml.zeit.de/2007/02/Vita' not in cache
        ICMSContent('http://xml.zeit.de/2007/02/Vita')
        assert len(cache) == 5
        assert 'http://xml.zeit.de/2006/49/Young' not in cache
        assert 'http://xml.zeit.de/2007/01/Miami' in cache
        assert 'http://xml.zeit.de/2007/02/Vita' in cache
        ICMSContent('http://xml.zeit.de/2006/49/Young')
        ICMSContent('http://xml.zeit.de/2006/52/Stimmts')
        ICMSContent('http://xml.zeit.de/2007/01/Macher')
        assert len(cache) == 5
        assert 'http://xml.zeit.de/2007/02/Vita' in cache
        assert 'http://xml.zeit.de/2006/49/Young' in cache
        assert 'http://xml.zeit.de/2007/01/Miami' not in cache

    def test_cache_info(self):
        assert caching.info() == {'size': 5, 'count': 0, 'hits': 0, 'misses': 0, 'usage': {}}
        ICMSContent('http://xml.zeit.de/2006/49/Young')
        ICMSContent('http://xml.zeit.de/2006/52/Stimmts')
        ICMSContent('http://xml.zeit.de/2007/01/Macher')
        assert caching.info() == {
            'size': 5,
            'count': 3,
            'hits': 0,
            'misses': 3,
            'usage': {
                'http://xml.zeit.de/2006/49/Young': 1,
                'http://xml.zeit.de/2006/52/Stimmts': 1,
                'http://xml.zeit.de/2007/01/Macher': 1,
            },
        }
        ICMSContent('http://xml.zeit.de/2006/52/Stimmts')
        ICMSContent('http://xml.zeit.de/2007/01/Macher')
        ICMSContent('http://xml.zeit.de/2007/02/Vita')
        assert caching.info() == {
            'size': 5,
            'count': 4,
            'hits': 2,
            'misses': 4,
            'usage': {
                'http://xml.zeit.de/2006/49/Young': 1,
                'http://xml.zeit.de/2006/52/Stimmts': 2,
                'http://xml.zeit.de/2007/01/Macher': 2,
                'http://xml.zeit.de/2007/02/Vita': 1,
            },
        }
