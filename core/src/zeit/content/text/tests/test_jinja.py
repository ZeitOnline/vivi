import zeit.content.text.jinja
import zeit.content.text.testing


class PythonScriptTest(zeit.content.text.testing.FunctionalTestCase):

    def create(self, text):
        result = zeit.content.text.jinja.JinjaTemplate()
        result.uniqueId = 'http://xml.zeit.de/template'
        result.text = text
        return result

    def test_renders_template(self):
        tpl = self.create('{{foo}}')
        self.assertEqual('bar', tpl({'foo': 'bar'}))

        tpl = self.create('{{fo}}')
        self.assertEqual('', tpl({'foo': 'bar'}))

        tpl = self.create('{{fo()}')
        self.assertIn(
            "jinja2.exceptions.TemplateSyntaxError: unexpected '}'",
            tpl({}))

        tpl = self.create('{{fo()}}')
        self.assertIn(
            "jinja2.exceptions.UndefinedError: \'fo\' is undefined",
            tpl({}))

    def test_mockdict_responds_to_any_variable(self):
        tpl = self.create('{{foo.bar.baz}}')
        self.assertIn('<MagicMock', tpl(zeit.content.text.jinja.MockDict()))
