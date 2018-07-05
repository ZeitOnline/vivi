from unittest import TestCase
from zope.component import getUtility
from zeit.find.elastic import ICMSSearch
from zeit.find.tests import LAYER


class TestElasticsearch(TestCase):

    layer = LAYER

    def test_cms_search_utility(self):
        cms_search = getUtility(ICMSSearch)
        assert cms_search.index == 'foo_pool'
