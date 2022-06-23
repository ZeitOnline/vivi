import json
import sys
import traceback
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

    def test_mockdict_responds_to_any_variable(self):
        tpl = self.create('{{foo.bar.baz}}')
        self.assertIn('<MagicMock', tpl(zeit.content.text.jinja.MockDict()))

    def test_runtime_error_rewrites_traceback(self):
        # Since we copied Template.render() wholesale from upstream,
        # we want to make sure we did not break anything by doing that.
        tpl = self.create('{{foo()}}')
        try:
            tpl({'foo': lambda: [][0]})
        except IndexError:
            self.assertEllipsis(
                '...File "<template>", line ... in top-level template code...',
                ''.join(traceback.format_exception(*sys.exc_info())))
        else:
            self.fail('did not raise')

    def test_escapes_variables_for_json(self):
        tpl = self.create("""{
            "title": "{{foo}}",
            "undefined": "{{nonexistent}}"
        }""")
        result = tpl({'foo': 'with "quotes"'}, output_format='json')
        result = json.loads(result)
        self.assertEqual({'title': 'with "quotes"', 'undefined': ''}, result)
