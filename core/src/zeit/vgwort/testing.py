import os
import unittest

import plone.testing
import pytest
import zope.component
import zope.index.text.interfaces
import zope.interface

import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.cms.webtest
import zeit.connector
import zeit.connector.testing
import zeit.content.author.testing
import zeit.vgwort.interfaces


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'vgwort-url': 'https://tom-test.vgwort.de/',
        'username': os.environ.get('ZEIT_VGWORT_USERNAME', ''),
        'password': os.environ.get('ZEIT_VGWORT_PASSWORD', ''),
        'minimum-token-amount': '10',
        'order-token-amount': '1',
        'days-before-report': '7',
        'days-age-limit-report': '10',
        'query-timeout': '1000',
        'claim-token-url': 'http://user:userpw@localhost/',
    },
    bases=(zeit.content.author.testing.CONFIG_LAYER,),
)
ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting-mock.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


SQL_ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting-mock.zcml',
    features=['zeit.connector.sql'],
    bases=(CONFIG_LAYER, zeit.connector.testing.SQL_CONFIG_LAYER),
)
SQL_ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(SQL_ZCML_LAYER,))
SQL_CONNECTOR_LAYER = zeit.connector.testing.SQLDatabaseLayer(bases=(SQL_ZOPE_LAYER,))


class XMLRPCLayer(plone.testing.Layer):
    defaultBases = (WSGI_LAYER,)

    def setUp(self):
        super().setUp()
        token_service = zeit.vgwort.token.TokenService()
        token_service.ServerProxy = lambda x: zeit.cms.webtest.ServerProxy(x, self['wsgi_app'])
        zope.component.getSiteManager().registerUtility(token_service)


XMLRPC_LAYER = XMLRPCLayer()

SOAP_ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting-soap.zcml', bases=(CONFIG_LAYER,))
SOAP_LAYER = zeit.cms.testing.ZopeLayer(bases=(SOAP_ZCML_LAYER,))


class TestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class SQLTestCase(zeit.connector.testing.TestCase):
    layer = SQL_CONNECTOR_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


@pytest.mark.integration()
class EndToEndTestCase(zeit.cms.testing.FunctionalTestCase, unittest.TestCase):
    layer = SOAP_LAYER
    level = 2

    def setUp(self):
        super().setUp()
        service = zope.component.getUtility(zeit.vgwort.interfaces.IMessageService)
        try:
            service.call('qualityControl')
        except Exception:
            self.skipTest('vgwort test system is down')


@zope.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@zope.interface.implementer(zope.index.text.interfaces.ISearchableText)
class SearchableText:
    def __init__(self, context):
        self.context = context

    def getSearchableText(self):
        return [self.context.teaserText or '']
