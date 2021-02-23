from mock import patch
from os import environ
from pathlib import Path
from transaction import commit
from zeit.cms.content import caching
from zeit.cms.interfaces import ICMSContent
from zeit.cms.repository.interfaces import IRepository
from zeit.cms.testing import ZeitCmsTestCase
from zope.component import getUtility, getGlobalSiteManager
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
            type(repository), 'getContent', wraps=repository.getContent)
        self.getcontent = self.getcontent_patch.start()
        self.getproperty_patch = patch(
            'zeit.cms.content.dav.CollectionTextLineProperty.fromProperty',
            return_value=('Icke', 'Er'))
        self.getproperty = self.getproperty_patch.start()
        self.path = Path(path)

    def tearDown(self):
        self.getproperty_patch.stop()
        self.getcontent_patch.stop()
        cache = vars(caching)['__cache']    # reset the cache by removing
        if hasattr(cache, 'cache'):         # the `cache` attribute
            delattr(cache, 'cache')
        super().tearDown()

    def test_content_is_cached(self):
        assert self.getcontent.call_count == 0
        a = ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 1
        commit()                            # new transaction (aka request)
        b = ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 1
        assert a is b

    def test_content_is_invalidated_by_update(self):
        a = ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 1
        commit()                            # new transaction (aka request)
        self.path.joinpath('testcontent').touch()
        b = ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 2
        assert a is not b

    def test_dav_properties_are_cached(self):
        assert self.getproperty.call_count == 0
        a = ICMSContent('http://xml.zeit.de/testcontent')
        assert a.authors == ('Icke', 'Er')
        assert self.getproperty.call_count == 1
        commit()                            # new transaction (aka request)
        b = ICMSContent('http://xml.zeit.de/testcontent')
        assert b.authors == ('Icke', 'Er')
        assert self.getproperty.call_count == 1

    def test_dav_properties_are_invalidated_by_update(self):
        a = ICMSContent('http://xml.zeit.de/testcontent')
        assert a.authors == ('Icke', 'Er')
        assert self.getproperty.call_count == 1
        commit()                            # new transaction (aka request)
        self.path.joinpath('testcontent.meta').touch()
        b = ICMSContent('http://xml.zeit.de/testcontent')
        assert b.authors == ('Icke', 'Er')
        assert self.getproperty.call_count == 2

    def test_least_used_content_is_removed(self):
        NotImplemented

    def test_cache_info(self):
        NotImplemented
