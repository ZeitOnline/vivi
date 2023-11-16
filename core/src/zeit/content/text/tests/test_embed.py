import zeit.content.text.embed
import zeit.content.text.testing
import zope.schema


class EmbedParameters(zeit.content.text.testing.FunctionalTestCase):
    def create(self, params):
        result = zeit.content.text.embed.Embed()
        result.uniqueId = 'http://xml.zeit.de/foo'
        result.parameter_definition = params
        return result

    def test_evaluates_parameter_definition_as_schema_fields(self):
        embed = self.create('{"one": zope.schema.TextLine()}')
        params = embed.parameter_fields
        field = params['one']
        self.assertIsInstance(field, zope.schema.TextLine)
        self.assertEqual('one', field.__name__)  # formlib needs this
        self.assertEqual('One', field.title)  # nice display default

    def test_supports_statements_and_custom_return(self):
        embed = self.create(
            """\
foo = "one"
__return({foo: zope.schema.TextLine()})
"""
        )
        params = embed.parameter_fields
        field = params['one']
        self.assertIsInstance(field, zope.schema.TextLine)

    def test_imports_required_packages(self):
        embed = self.create('collections.OrderedDict([("one", zope.schema.TextLine())])')
        params = embed.parameter_fields
        field = params['one']
        self.assertIsInstance(field, zope.schema.TextLine)

    def test_errors_are_ignored_silently(self):
        embed = self.create('{"one": zope.schema.TextLin()}')
        self.assertEqual({}, embed.parameter_fields)
        embed = self.create('{"one": zope.schema.TextLine()')
        self.assertEqual({}, embed.parameter_fields)

    def test_invalid_values_are_dropped(self):
        embed = self.create('[zope.schema.TextLine()]')
        self.assertEqual({}, embed.parameter_fields)
        embed = self.create('{"one": "not a field", "two": zope.schema.TextLine()}')
        self.assertEqual(['two'], list(embed.parameter_fields.keys()))
