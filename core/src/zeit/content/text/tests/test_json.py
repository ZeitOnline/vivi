import zeit.cms.checkout.helper
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

        schema, registry = validation._get()
        pattern = '^((\\{urn:uuid:)?([a-f0-9]{8})\\}?)$'
        self.assertEqual(pattern, schema['components']['schemas']['uuid']['pattern'])
        self.assertEqual(
            pattern,
            registry[validation.schema_url].contents['components']['schemas']['uuid']['pattern'],
        )

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


class JSONTestCase(zeit.content.text.testing.FunctionalTestCase):
    def test_json_supports_comments(self):
        json_content = zeit.content.text.json.JSON()
        json_content.text = '// this is a comment\n["{urn:uuid:d995ba5a}"]'
        self.repository['json'] = json_content
        with zeit.cms.checkout.helper.checked_out(self.repository['json']):
            pass
        content = self.repository['json']
        self.assertEqual(content.text, '// this is a comment\n["{urn:uuid:d995ba5a}"]')
        self.assertEqual(content.data, ['{urn:uuid:d995ba5a}'])
