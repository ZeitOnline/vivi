# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.cp.tests


def create_cp(browser, filename='island'):
    browser.open('http://localhost/++skin++cms/repository/online/2007/01')

    menu = browser.getControl(name='add_menu')
    menu.displayValue = ['CenterPage']
    browser.open(menu.value[0])

    browser.getControl('File name').value = filename
    browser.getControl('Title').value = 'Auf den Spuren der Elfen'
    browser.getControl('Ressort').displayValue = ['Reisen']
    browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
    browser.getControl(name="form.actions.add").click()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'teaser.txt',
        checker=zeit.content.cp.tests.checker,
        layer=zeit.content.cp.tests.layer))
    return suite
