# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'adapter.txt',
        'keyword.txt',
        'property.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS),
        setUp=zeit.cms.testing.setUp,
        package='zeit.cms.content'))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'dav.txt',
        'field.txt',
        'liveproperty.txt',
        'lxmlpickle.txt',
        'metadata.txt',
        'semanticchange.txt',
        'sources.txt',
        'xmlsupport.txt',
        'contentuuid.txt',
        package='zeit.cms.content'))
    return suite
