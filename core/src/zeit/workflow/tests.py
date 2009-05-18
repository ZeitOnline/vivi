# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import __future__
import os
import os.path
import stat
import tempfile
import unittest
import zeit.cms.testing
import zope.app.testing.functional


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
    'news-channel': 'http://xml.zeit.de/politik.feed',
}

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'autosynd.txt',
        'dependency.txt',
        'syndication.txt',
        layer=WorkflowLayer,
        product_config={'zeit.workflow': product_config},
        globs={'with_statement': __future__.with_statement}))
    return suite
