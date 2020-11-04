import jinja2.exceptions
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

    def test_error_template_should_raise(self):
        tpl = self.create('{{foo}')
        with self.assertRaises(jinja2.exceptions.TemplateSyntaxError):
            tpl({'foo': 'bar'})

    def test_mockdict_responds_to_any_variable(self):
        tpl = self.create('{{foo.bar.baz}}')
        self.assertIn('<MagicMock', tpl(zeit.content.text.jinja.MockDict()))
