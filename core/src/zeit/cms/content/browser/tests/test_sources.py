# coding: utf-8
import json
import urllib.parse

import zope.browser.interfaces
import zope.component
import zope.publisher.browser

import zeit.cms.testing


class SourceSecurityTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def setUp(self):
        super().setUp()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent/@@checkout')
        b.getControl('Year').value = '2008'
        b.getControl('Ressort').displayValue = ['International']
        b.getControl('Title').value = 'foo'

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
        self.browser.open('http://localhost/@@source?name=zeit.cms.content.interfaces.AccessSource')
        self.assert_json(
            [
                {'id': 'free', 'title': 'access-free'},
                {'id': 'registration', 'title': 'access-registration'},
                {'id': 'abo', 'title': 'access-abo'},
                {'id': 'dynamic', 'title': 'access-dynamic'},
            ]
        )

    def test_uses_id_for_object_source(self):
        b = self.browser
        b.open('http://localhost/@@source?name=zeit.cms.content.sources.ProductSource')
        data = json.loads(b.contents)
        self.assertIn({'id': 'ZEDE', 'title': 'Online'}, data)

    def test_allows_configuring_short_names(self):
        b = self.browser
        b.open('http://localhost/@@source?name=product')
        data = json.loads(b.contents)
        self.assertIn({'id': 'ZEDE', 'title': 'Online'}, data)

    def test_serializes_subressorts(self):
        b = self.browser
        b.open('http://localhost/@@source?name=zeit.cms.content.sources.RessortSource')
        data = json.loads(b.contents)
        row = data[0]
        self.assertEqual('deutschland', row['id'])
        self.assertEqual('Deutschland', row['title'])
        self.assertEqual(4, len(row['children']))
        self.assertEqual('integration', row['children'][0]['id'])


class SubnavigationTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_unknown_value_returns_empty_list(self):
        b = self.browser
        token = self._get_token('nonexistent')
        b.open(f'/repository/@@subnavigationupdater.json?parent_token={token}')
        self.assertEqual([], json.loads(b.contents))

    def test_returns_child_values_for_parent(self):
        b = self.browser
        token = self._get_token('Deutschland')
        b.open(f'/repository/@@subnavigationupdater.json?parent_token={token}')

        data = json.loads(b.contents)
        self.assertEqual(
            ['Datenschutz', 'Integration', 'Joschka Fisher', 'Meinung'], [x[0] for x in data]
        )

        self.assertEqual('public;max-age=3600', b.headers['Cache-Control'])

    @staticmethod
    def _get_token(value):
        source = zeit.cms.content.interfaces.ICommonMetadata['ressort'].source(None)
        request = zope.publisher.browser.TestRequest()
        terms = zope.component.getMultiAdapter((source, request), zope.browser.interfaces.ITerms)
        token = terms.getTerm(value).token
        return urllib.parse.quote(token)
