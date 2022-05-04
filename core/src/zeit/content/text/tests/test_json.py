from jsonschema.exceptions import ValidationError

import commentjson

import zeit.content.text.interfaces
import zeit.content.text.testing


class JSONValidationTestCase(zeit.content.text.testing.FunctionalTestCase):

    schema = commentjson.dumps({'uuid': {
        'type': 'string',
        'pattern':
            "^((\\{urn:uuid:)?([a-f0-9]{8})\\}?)$"}
    })

    def test_provide_schema_for_validation(self):
        json_content = zeit.content.text.json.JSON()
        validation = zeit.content.text.interfaces.IValidationSchema(
            json_content)
        validation.json_schema = self.schema
        validation.field = 'uuid'
        self.assertEqual('uuid', validation.field)
        self.assertEqual(self.schema, validation.json_schema)

    def test_validate_json_against_schema(self):
        json_content = zeit.content.text.json.JSON()
        json_content.text = '"{urn:uuid:!noid!}"'
        validation = zeit.content.text.interfaces.IValidationSchema(
            json_content)
        validation.json_schema = self.schema
        validation.field = 'uuid'
        with self.assertRaises(ValidationError):
            json_content.validate_data()
        json_content.text = '"{urn:uuid:d995ba5a}"'
        json_content.validate_data()

    def test_schema_reference_resolver_should_work(self):
        json_content = zeit.content.text.json.JSON()
        json_content.text = '["{urn:uuid:d995ba5a}"]'
        validation = zeit.content.text.interfaces.IValidationSchema(
            json_content)
        validation.json_schema = commentjson.dumps({
            'overlord': {
                'type': 'array',
                'items': {
                    '$ref': '#/components/schemas/uuid'
                }
            },
            'uuid': {
                'type': 'string',
                'pattern':
                    "^((\\{urn:uuid:)?([a-f0-9]{8})\\}?)$"}})
        validation.field = 'overlord'
        json_content.validate_data()
