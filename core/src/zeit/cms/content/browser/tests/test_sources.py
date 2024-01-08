# coding: utf-8
import json

import zeit.cms.testing


class SourceSecurityTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def setUp(self):
        super().setUp()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent/@@checkout')
        b.getControl('Year').value = '2008'
        b.getControl('Ressort').displayValue = ['International']
        b.getControl('Title').value = 'foo'
        b.getControl(name='form.authors.0.').value = 'asdf'

    def test_product_works_with_security(self):
        b = self.browser
        b.getControl('Product id').displayValue = ['Zeit Campus']
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual(['Zeit Campus'], b.getControl('Product id').displayValue)

    def test_serie_works_with_security(self):
        b = self.browser
        b.getControl('Serie').displayValue = ['Autotest']
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual(['Autotest'], b.getControl('Serie').displayValue)


class SourceAPI(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_serializes_source_to_json(self):
        self.browser.open('http://localhost/@@source' '?name=zeit.cms.content.sources.AccessSource')
        self.assert_json(
            [
                {'id': 'free', 'title': 'frei verfügbar'},
                {'id': 'registration', 'title': 'registrierungspflichtig'},
                {'id': 'dynamic', 'title': 'dynamisch'},
                {'id': 'abo', 'title': 'abopflichtig'},
            ]
        )

    def test_uses_id_for_object_source(self):
        b = self.browser
        b.open('http://localhost/@@source' '?name=zeit.cms.content.sources.ProductSource')
        data = json.loads(b.contents)
        self.assertIn({'id': 'ZEDE', 'title': 'Zeit Online'}, data)

    def test_allows_configuring_short_names(self):
        b = self.browser
        b.open('http://localhost/@@source?name=product')
        data = json.loads(b.contents)
        self.assertIn({'id': 'ZEDE', 'title': 'Zeit Online'}, data)

    def test_serializes_subressorts(self):
        b = self.browser
        b.open('http://localhost/@@source' '?name=zeit.cms.content.sources.RessortSource')
        data = json.loads(b.contents)
        row = data[0]
        self.assertEqual('deutschland', row['id'])
        self.assertEqual('Deutschland', row['title'])
        self.assertEqual(4, len(row['children']))
        self.assertEqual('integration', row['children'][0]['id'])
