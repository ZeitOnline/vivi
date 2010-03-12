# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.DocFileSuite(
        'adapter.txt',
        'property.txt',
        package='zeit.cms.content'))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'contentuuid.txt',
        'dav.txt',
        'field.txt',
        'keyword.txt',
        'liveproperty.txt',
        'lxmlpickle.txt',
        'metadata.txt',
        'semanticchange.txt',
        'sources.txt',
        'xmlsupport.txt',
        package='zeit.cms.content'))
    return suite
