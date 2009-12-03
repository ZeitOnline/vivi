# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import unittest
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zeit.wysiwyg.html
import zope.app.testing.functional


WYSIWYGLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'WYSIWYGLayer', allow_teardown=True)


class HTMLContent(zeit.wysiwyg.html.HTMLContentBase):

    zope.component.adapts(
        zeit.cms.testcontenttype.interfaces.ITestContentType)

    def get_tree(self):
        return self.context.xml['body']


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'html.txt',
        'reference.txt',
        layer=WYSIWYGLayer))
    return suite
