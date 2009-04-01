# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import re
import sys
import zeit.connector.interfaces
import zope.app.appsetup.product
import zope.app.testing.functional
import zope.component
import zope.file.testing
import zope.testing.renormalizing
from zope.testing import doctest


cms_layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'CMSLayer', allow_teardown=True)


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d'), '<FORMATTED DATE>'),
    (re.compile('0x[0-9a-f]+'), "0x..."),
])


def setUp(test):
    setup_product_config(test.globs.get('product_config', {}))


def tearDown(test):
    connector = zope.component.getUtility(
        zeit.connector.interfaces.IConnector)
    connector._reset()


def setup_product_config(product_config={}):
    zope.app.appsetup.product._configs.clear()
    cms_config = zope.app.appsetup.product._configs['zeit.cms'] = {}
    base_path = os.path.join(os.path.dirname(__file__), 'content')

    cms_config['source-serie'] = 'file://%s' % os.path.join(
        base_path, 'serie.xml')
    cms_config['source-navigation'] = 'file://%s' % os.path.join(
        base_path, 'navigation.xml')
    cms_config['source-print-ressort'] = 'file://%s' % os.path.join(
        base_path, 'print-ressort.xml')
    cms_config['source-keyword'] = 'file://%s' % os.path.join(
        base_path, 'zeit-ontologie-prism.xml')

    cms_config['preview-prefix'] = 'http://localhost/preview-prefix'
    cms_config['live-prefix'] = 'http://localhost/live-prefix'
    cms_config['development-preview-prefix'] = (
        'http://localhost/development-preview-prefix')
    cms_config['workingcopy-preview-base'] = (
        u'http://xml.zeit.de/tmp/previews/')

    cms_config['suggest-keyword-email-address'] = 'none@testing'
    cms_config['suggest-keyword-real-name'] = 'Dr. No'

    zope.app.appsetup.product._configs.update(product_config)


optionflags = (doctest.REPORT_NDIFF +
               doctest.INTERPRET_FOOTNOTES +
               doctest.NORMALIZE_WHITESPACE +
               doctest.ELLIPSIS)


def FunctionalDocFileSuite(*paths, **kw):
    layer = kw.pop('layer', cms_layer)
    kw['package'] = doctest._normalize_module(kw.get('package'))
    kw['setUp'] = setUp
    kw['tearDown'] = tearDown
    kw.setdefault('globs', {})['product_config'] = kw.pop(
        'product_config', {})
    kw.setdefault('checker', checker)
    kw.setdefault('optionflags', optionflags)

    test = zope.file.testing.FunctionalBlobDocFileSuite(
        *paths, **kw)
    test.layer = layer

    return test


def click_wo_redirect(browser, *args, **kwargs):
    import urllib2
    browser.mech_browser.set_handle_redirect(False)
    try:
        try:
            browser.getLink(*args, **kwargs).click()
        except urllib2.HTTPError, e:
            print str(e)
            print e.hdrs.get('location')
    finally:
        browser.mech_browser.set_handle_redirect(True)


