import zeit.cms.testing
import zeit.content.text.jinja
import zeit.content.text.testing


class PythonScriptTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.text.testing.ZCML_LAYER

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
