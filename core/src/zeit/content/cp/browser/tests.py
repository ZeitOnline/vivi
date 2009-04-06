# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.cp.tests
import z3c.etestbrowser.testing


def open_cp():
    browser = z3c.etestbrowser.testing.ExtendedTestBrowser()
    browser.addHeader('Authorization', 'Basic user:userpw')
    browser.open('http://localhost/++skin++cms/repository/online/2007/01')

    menu = browser.getControl(name='add_menu')
    menu.displayValue = ['CenterPage']
    browser.open(menu.value[0])

    browser.getControl('File name').value = 'island'
    browser.getControl('Title').value = 'Auf den Spuren der Elfen'
    browser.getControl('Ressort').displayValue = ['Reisen']
    browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
    browser.getControl(name="form.actions.add").click()
    browser.getLink('Edit contents').click()
    return browser


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'teaser.txt',
        checker=zeit.content.cp.tests.checker,
        layer=zeit.content.cp.tests.layer))
    return suite
