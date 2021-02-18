from mock import patch
from os import environ
from pathlib import Path
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
        self.path = Path(path)

    def tearDown(self):
        self.getcontent_patch.stop()
        cache = vars(caching)['__cache']    # reset the cache by removing
        if hasattr(cache, 'cache'):         # the `cache` attribute
            delattr(cache, 'cache')
        super().tearDown()

    def test_content_is_cached(self):
        assert self.getcontent.call_count == 0
        ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 1
        ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 1

    def test_content_is_invalidated_by_update(self):
        ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 1
        self.path.joinpath('testcontent').touch()
        ICMSContent('http://xml.zeit.de/testcontent')
        assert self.getcontent.call_count == 2

    def test_dav_properties_are_cached(self):
        NotImplemented

    def test_dav_properties_are_invalidated_by_update(self):
        NotImplemented

    def test_least_used_content_is_removed(self):
        NotImplemented

    def test_cache_info(self):
        NotImplemented
