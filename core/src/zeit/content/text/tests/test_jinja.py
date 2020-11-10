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

    def test_template_syntax_error_should_return_formatted_exception(self):
        tpl = self.create('{{foo}')
        self.assertEqual(
            "Traceback (most recent call last):\n" +
            "jinja2.exceptions.TemplateSyntaxError: unexpected '}'\n",
            tpl({'foo': 'bar'}))

    def test_not_callable_str_should_return_formatted_exception(self):
        tpl = self.create('{{foo()}}')
        self.assertEqual(
            "Traceback (most recent call last):\n  " +
            "Module zeit.content.text.jinja, line 49, in &lt;genexpr&gt;" +
            "\n    return ''.join(str(value) for value in " +
            "self.root_render_func(\n  Module &lt;template&gt;, " +
            "line 1, in top-level template code\nTypeError: 'str' " +
            "object is not callable\n",
            tpl({'foo': 'bar'}))

    def test_mockdict_responds_to_any_variable(self):
        tpl = self.create('{{foo.bar.baz}}')
        self.assertIn('<MagicMock', tpl(zeit.content.text.jinja.MockDict()))
