from jsonschema.exceptions import ValidationError

import mock
import requests_mock
import yaml

import zeit.content.text.interfaces
import zeit.content.text.json
import zeit.content.text.testing


class JSONValidationTestCase(zeit.content.text.testing.FunctionalTestCase):

    schema_json = {'components': {
        'schemas': {
            'UUID': {
                'type': 'string',
                'pattern':
                    "^((\\{urn:uuid:)?([a-f0-9]{8})\\}?)$"}
        }
    }}

    def test_get_schema_from_url(self):
        json_content = zeit.content.text.json.JSON()
        validation = zeit.content.text.interfaces.IValidationSchema(
            json_content)
        validation.schema_url = (
            'https://testschema.zeit.de/openapi.yaml')

        with requests_mock.Mocker() as r_mock:
            r_mock.register_uri(
                'GET', 'https://testschema.zeit.de/openapi.yaml',
                text=yaml.safe_dump(self.schema_json))
            schema = json_content.get_schema()

        self.assertEqual(self.schema_json, schema)

    def test_validate_data_against_schema(self):
        json_content = zeit.content.text.json.JSON()
        json_content.text = '{"UUID": "{urn:uuid:!noid!}"}'

        with mock.patch('zeit.content.text.json.JSON.get_schema') as schema:
            schema.return_value = self.schema_json

            with self.assertRaises(ValidationError):
                json_content.validate_data_against_schema()

            json_content.text = '{"UUID": "{urn:uuid:d995ba5a}"}'
            json_content.validate_data_against_schema()
