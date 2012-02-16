# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import __future__
import re
import shutil
import tempfile
import unittest
import zeit.cms.testing
import zeit.content.cp.testing
import zeit.workflow.testing
import zope.testing.renormalizing


product_config = """
<product-config zeit.content.article>
    cds-import-valid-path $$ressort/$$year/$$volume
    cds-import-invalid-path cds/invalid/$$year/$$volume
</product-config>
"""


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>"),])
checker.transformers[0:0] = zeit.cms.testing.checker.transformers


ArticleLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(
        product_config +
        zeit.workflow.testing.product_config +
        zeit.content.cp.testing.product_config +
        zeit.cms.testing.cms_product_config))


CDSZCMLLayer = zeit.cms.testing.ZCMLLayer(
    'cds_ftesting.zcml',
    product_config=(
        product_config +
        zeit.workflow.testing.product_config +
        zeit.content.cp.testing.product_config +
        zeit.cms.testing.cms_product_config))


class CDSLayer(CDSZCMLLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        product_config = zope.app.appsetup.product._configs[
            'zeit.content.article']
        product_config['cds-export'] = tempfile.mkdtemp()
        product_config['cds-import'] = tempfile.mkdtemp()

    @classmethod
    def testTearDown(cls):
        product_config = zope.app.appsetup.product._configs[
            'zeit.content.article']
        # I don't know why, but those directories get removed automatically
        # somehow.
        try:
            shutil.rmtree(product_config['cds-export'])
        except OSError:
            pass
        try:
            shutil.rmtree(product_config['cds-import'])
        except OSError:
            pass
        del product_config['cds-export']
        del product_config['cds-import']


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'pagebreak.txt',
        'recension.txt',
        layer=ArticleLayer))

    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'cds_export.txt',
        'cds_import.txt',
        'layout.txt',
        layer=CDSLayer,
        checker=checker,
        globs={'with_statement': __future__.with_statement}))
    return suite
