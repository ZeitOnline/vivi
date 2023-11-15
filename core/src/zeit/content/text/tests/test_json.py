import zeit.content.text.interfaces
import zeit.content.text.json
import zeit.content.text.testing


class JSONValidationTestCase(zeit.content.text.testing.FunctionalTestCase):
    def test_only_validate_if_field_in_schema(self):
        json_content = zeit.content.text.json.JSON()
        validation = zeit.content.text.interfaces.IValidationSchema(json_content)
        validation.schema_url = zeit.content.text.testing.schema_url
        validation.field_name = 'evil'
        with self.assertRaises(zeit.content.text.interfaces.SchemaValidationError):
            validation.validate()

    def test_get_schema_from_url(self):
        json_content = zeit.content.text.json.JSON()
        validation = zeit.content.text.interfaces.IValidationSchema(json_content)
        validation.schema_url = zeit.content.text.testing.schema_url
        validation.field_name = 'uuid'

        schema, ref_resolver = validation._get()
        pattern = '^((\\{urn:uuid:)?([a-f0-9]{8})\\}?)$'
        self.assertEqual(pattern, schema['components']['schemas']['uuid']['pattern'])
        self.assertEqual(pattern, ref_resolver.referrer['components']['schemas']['uuid']['pattern'])

    def test_validate_data_against_schema(self):
        json_content = zeit.content.text.json.JSON()
        json_content.text = '"{urn:uuid:!noid!}"'
        validation = zeit.content.text.interfaces.IValidationSchema(json_content)
        validation.schema_url = zeit.content.text.testing.schema_url
        validation.field_name = 'uuid'
        with self.assertRaises(zeit.content.text.interfaces.SchemaValidationError):
            validation.validate()
        json_content.text = '"{urn:uuid:d995ba5a}"'
        validation.validate()

    def test_schema_reference_resolver_should_work(self):
        json_content = zeit.content.text.json.JSON()
        json_content.text = '["{urn:uuid:d995ba5a}"]'
        validation = zeit.content.text.interfaces.IValidationSchema(json_content)
        validation.schema_url = zeit.content.text.testing.schema_url
        validation.field_name = 'overlord'
        validation.validate()
