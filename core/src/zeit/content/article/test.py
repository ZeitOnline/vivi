# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import __future__
import shutil
import tempfile
import unittest
import os
import re
import zeit.cms.testing
import zope.app.testing.functional
import zope.testing.renormalizing
from zope.testing import doctest

product_config = {
    'cds-import-valid-path': 'online',
    'cds-import-invalid-path': 'cds/invalid',
}

checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>"),])

ArticleLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ArticleLayer', allow_teardown=True)

class CDSLayerFactory(zope.app.testing.functional.ZCMLLayer):

    def __init__(self):
        zope.app.testing.functional.ZCMLLayer.__init__(
            self, os.path.join(os.path.dirname(__file__),
                               'cds_ftesting.zcml'),
            __name__, 'CDSLayer', allow_teardown=True)

    def setUp(self):
        zope.app.testing.functional.ZCMLLayer.setUp(self)
        product_config['cds-export'] = tempfile.mkdtemp()
        product_config['cds-import'] = tempfile.mkdtemp()

    def tearDown(self):
        zope.app.testing.functional.ZCMLLayer.tearDown(self)
        shutil.rmtree(product_config['cds-export'])
        shutil.rmtree(product_config['cds-import'])
        del product_config['cds-export']
        del product_config['cds-import']

CDSLayer = CDSLayerFactory()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'recension.txt',
        layer=ArticleLayer))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'cds_export.txt',
        'cds_import.txt',
        layer=CDSLayer,
        checker=checker,
        product_config={'zeit.content.article': product_config,
                        'zeit.workflow': {'publish-script': 'cat',
                                          'path-prefix': ''}},
        globs={'with_statement': __future__.with_statement}))
    return suite
