# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os

from zope.testing import doctest

import zope.component

import zope.app.testing.functional
import zope.app.appsetup.product

import zeit.connector.interfaces


cms_layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'CMSLayer', allow_teardown=True)


def setUp(test):
    setup_product_config()


def setup_product_config():
    cms_config = zope.app.appsetup.product._configs['zeit.cms'] = {}
    base_path = os.path.join(os.path.dirname(__file__), 'content')

    cms_config['source-serie'] = 'file://%s' % os.path.join(
        base_path, 'serie.xml')
    cms_config['source-ressort'] = 'file://%s' % os.path.join(
        base_path, 'ressort.xml')
    cms_config['source-print-ressort'] = 'file://%s' % os.path.join(
        base_path, 'ressort.xml')
    cms_config['source-keyword'] = 'file://%s' % os.path.join(
        base_path, 'zeit-ontologie-prism.xml')

    cms_config['preview-prefix'] = 'http://localhost/preview-prefix'
    cms_config['live-prefix'] = 'http://localhost/live-prefix'
    cms_config['development-preview-prefix'] = (
        'http://localhost/development-preview-prefix')
    cms_config['workingcopy-preview-base'] = u'http://xml.zeit.de/tmp/previews'


def FunctionalDocFileSuite(*paths, **kw):
    try:
        layer = kw['layer']
    except KeyError:
        layer = cms_layer
    else:
        del kw['layer']
    kw['package'] = doctest._normalize_module(kw.get('package'))
    kw['setUp'] = setUp

    def tearDown(test):
        zope.app.testing.functional.FunctionalTestSetup().tearDown()
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector._reset()
    kw['tearDown'] = tearDown

    test = zope.app.testing.functional.FunctionalDocFileSuite(
        *paths, **kw)
    test.layer = layer
    return test
