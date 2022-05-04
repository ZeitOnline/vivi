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
