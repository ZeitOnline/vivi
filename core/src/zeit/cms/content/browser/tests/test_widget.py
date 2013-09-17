# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class MobileAlternativeWidgetTest(zeit.cms.testing.BrowserTestCase):

    def _set_default_values(self, browser):
        b = browser
        b.getControl('Year').value = '2008'
        b.getControl('Ressort').displayValue = ['International']
        b.getControl('Title').value = 'foo'
        b.getControl(name='form.authors.0.').value = 'asdf'

    def test_stores_given_url(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/testcontent/@@checkout')
        self._set_default_values(b)
        MOBILE_URL = 'http://example.com'
        b.getControl('Mobile URL').value = MOBILE_URL
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        content = self.layer.setup.getRootFolder()[
            'workingcopy']['zope.user']['testcontent']
        self.assertEqual(
            MOBILE_URL, content.mobile_alternative)
        self.assertEqual(MOBILE_URL, b.getControl('Mobile URL').value)

    def test_setting_checkbox_stores_www_url_but_displays_no_url(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/testcontent/@@checkout')
        self._set_default_values(b)
        b.getControl('no mobile alternative').selected = True
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        content = self.layer.setup.getRootFolder()[
            'workingcopy']['zope.user']['testcontent']
        self.assertEqual(
            'http://www.zeit.de/testcontent', content.mobile_alternative)
        self.assertEqual('', b.getControl('Mobile URL').value)
        self.assertEqual(True, b.getControl('no mobile alternative').selected)
