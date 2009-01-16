# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import unittest

from zope.testing import doctest

import zeit.cms.testing

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'form.txt',
        'keyword.txt',
        'template.txt',
        'typechange.txt',
        'widget-subnav.txt'))
    suite.addTest(doctest.DocFileSuite(
        'widget.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS)))
    return suite
