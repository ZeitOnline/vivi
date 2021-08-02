"""XXX This should probably be include in zeit.retresco.testing, but that
doesn't work due to a circular test dependency between zeit.retresco and
zeit.content.article.
The Right Thing(tm) to do would probably be to abstract ITMS/IElasticsearch
and move them to zeit.cms (like we do with e.g. IPublish), but that's a lot of
busy work for (so far) not _much_ gain.
"""
from unittest import mock
import plone.testing
import zeit.cms.interfaces
import zeit.retresco.interfaces
import zope.component
import zope.interface


class ElasticsearchMockLayer(plone.testing.Layer):

    def testSetUp(self):
        self['elasticsearch'] = mock.Mock()
        self['elasticsearch'].search.return_value = (
            zeit.cms.interfaces.Result())
        zope.interface.alsoProvides(
            self['elasticsearch'], zeit.retresco.interfaces.IElasticsearch)
        zope.component.getSiteManager().registerUtility(self['elasticsearch'])

    def testTearDown(self):
        zope.component.getSiteManager().unregisterUtility(
            self['elasticsearch'])
        del self['elasticsearch']


ELASTICSEARCH_MOCK_LAYER = ElasticsearchMockLayer()


class TMSMockLayer(plone.testing.Layer):

    def testSetUp(self):
        self['tms'] = mock.Mock()
        self['tms'].get_topicpage_documents.return_value = (
            zeit.cms.interfaces.Result())
        self['tms'].get_related_documents.return_value = (
            zeit.cms.interfaces.Result())
        zope.interface.alsoProvides(
            self['tms'], zeit.retresco.interfaces.ITMS)
        zope.component.getSiteManager().registerUtility(self['tms'])

    def testTearDown(self):
        zope.component.getSiteManager().unregisterUtility(self['tms'])
        del self['tms']


TMS_MOCK_LAYER = TMSMockLayer()
