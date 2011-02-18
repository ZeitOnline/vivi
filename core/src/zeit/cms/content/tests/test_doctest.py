# Copyright (c) 2007-2011 gocept gmbh & co. kg
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
        'dublincore.txt',
        'field.txt',
        'liveproperty.txt',
        'lxmlpickle.txt',
        'metadata.txt',
        'semanticchange.txt',
        'sources.txt',
        'xmlsupport.txt',
        package='zeit.cms.content'))
    return suite
