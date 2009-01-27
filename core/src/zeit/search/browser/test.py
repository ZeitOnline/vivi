# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import unittest
import zeit.search.test
import zeit.cms.selenium
from zope.testing import doctest

class Selenium(zeit.cms.selenium.Test):

    def test_toggle_extended_search(self):
        s = self.selenium
        self.open('/')
        # Initially extended is hidden
        s.verifyVisible('id=search-extended-show')
        s.verifyNotVisible('id=search-extended-form')
        # Show extended search
        s.click('id=search-extended-show')
        s.verifyNotVisible('id=search-extended-show')
        s.verifyVisible('id=search-extended-form')
        # State is kept when the page reloads
        self.open('/')
        s.verifyNotVisible('id=search-extended-show')
        s.verifyVisible('id=search-extended-form')
        # Hide
        s.click('id=search-extended-hide')
        s.verifyVisible('id=search-extended-show')
        s.verifyNotVisible('id=search-extended-form')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.search.test.SearchLayer,
        product_config=zeit.search.test.product_config))
    return suite
