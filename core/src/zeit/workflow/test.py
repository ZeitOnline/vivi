# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest
import stat
import tempfile

from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing


class WorkflowLayerFactory(zope.app.testing.functional.ZCMLLayer):
    """Layer which copies the publish/retract scripts and makes them
    executable."""

    def __init__(self, *args, **kwargs):
        zope.app.testing.functional.ZCMLLayer.__init__(self, *args, **kwargs)
        self._tempfiles = []

    def setUp(self):
        zope.app.testing.functional.ZCMLLayer.setUp(self)
        product_config['publish-script']  = self._make_copy('publish.sh')
        product_config['retract-script'] = self._make_copy('retract.sh')


    def tearDown(self):
        for name in self._tempfiles:
            os.remove(name)
        zope.app.testing.functional.ZCMLLayer.tearDown(self)

    def _make_copy(self, script):
        source = os.path.join(os.path.dirname(__file__), script)
        fd, destination = tempfile.mkstemp(suffix=script)
        self._tempfiles.append(destination)
        f = os.fdopen(fd, 'w')
        f.write(open(source).read())
        f.close()
        os.chmod(destination, stat.S_IRUSR|stat.S_IXUSR)
        return destination


WorkflowLayer = WorkflowLayerFactory(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'WorkflowLayer', allow_teardown=True)


product_config = {
    'path-prefix': 'work',
}

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'syndication.txt',
        layer=WorkflowLayer,
        product_config={'zeit.workflow': product_config},
        optionflags=(doctest.INTERPRET_FOOTNOTES|doctest.ELLIPSIS|
                     doctest.REPORT_NDIFF|doctest.NORMALIZE_WHITESPACE)))
    return suite
