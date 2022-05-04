import jsonschema.validators
import mock
import urllib.error

import zeit.cms.testing
import zeit.content.text.embed
import zeit.content.text.json
import zeit.content.text.testing


class JSONBrowserTest(zeit.content.text.testing.BrowserTestCase):

    def test_add_json(self):
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/2006')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['JSON file']
        b.open(menu.value[0])
        self.assertEllipsis('...Add JSON file...', b.contents)
        b.getControl('File name').value = 'foo'
        b.getControl('Content').value = '{"foo":'
        b.getControl('Add').click()
        self.assertEllipsis('...Unexpected token...', b.contents)

        b.getControl('Content').value = '{"foo": "bar"}'
        b.getControl('Add').click()
        self.assertEllipsis('...Edit JSON file...', b.contents)

        b.getControl('Content').value = '{"changed": "now"}'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        b.getLink('Checkin').click()
        self.assertEllipsis('...<pre>...changed...</pre>...', b.contents)


class JSONValidationTest(zeit.content.text.testing.BrowserTestCase):

    schema_json = {'components': {
        'schemas': {
            'uuid': {
                'type': 'string',
                'pattern':
                    "^((\\{urn:uuid:)?([a-f0-9]{8})\\}?)$"}
        }
    }}

    def test_validate_against_schema(self):
        self.repository['foo'] = zeit.content.text.json.JSON()
        browser = self.browser
        browser.open('http://localhost/++skin++cms/repository/foo')
        browser.getLink('Checkout').click()
        self.assertEllipsis('...Validate...', browser.contents)
        browser.getControl('Content').value = '"{urn:uuid:d995ba5a}"'
        browser.getControl('Apply').click()
        browser.getLink('Validate').click()
        browser.getControl('url of schema').value = (
            'http://testschema.zeit.de/schema.yaml')
        browser.getControl('specific schema to use for validation').value = (
            'uuid')
        browser.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', browser.contents)
        with mock.patch('zeit.content.text.json.JSON.get_schema') as schema:
            schema.return_value = (
                self.schema_json, jsonschema.validators.RefResolver.from_schema(
                    self.schema_json))
            browser.getLink('Checkin').click()
        self.assertEllipsis('...has been checked in...', browser.contents)

    def test_validation_error_results_in_checkin_error(self):
        self.repository['foo'] = zeit.content.text.json.JSON()
        browser = self.browser
        browser.open('http://localhost/++skin++cms/repository/foo')
        browser.getLink('Checkout').click()
        browser.getControl('Content').value = '"{uuid:d995ba5a}"'
        browser.getControl('Apply').click()
        browser.getLink('Validate').click()
        browser.getControl('url of schema').value = (
            'http://testschema.zeit.de/schema.yaml')
        browser.getControl('specific schema to use for validation').value = (
            'uuid')
        browser.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', browser.contents)
        with mock.patch('zeit.content.text.json.JSON.get_schema') as schema:
            schema.return_value = (
                self.schema_json, jsonschema.validators.RefResolver.from_schema(
                    self.schema_json))
            with self.assertRaises(urllib.error.HTTPError):
                browser.getLink('Checkin').click()
                self.assertEllipsis(
                    '...Failed validating...', browser.contents)
