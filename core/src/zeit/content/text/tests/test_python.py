import zeit.content.text.testing


class PythonScriptTest(zeit.content.text.testing.FunctionalTestCase):
    def create(self, text):
        py = zeit.content.text.python.PythonScript()
        py.uniqueId = 'http://xml.zeit.de/py'
        py.text = text
        return py

    def test_returns_value(self):
        py = self.create('__return(42)')
        self.assertEqual(42, py())

    def test_return_stops_execution(self):
        py = self.create(
            """\
__return(1)
__return(2)"""
        )
        self.assertEqual(1, py())

    def test_keyword_args_are_passed_in_as_context(self):
        py = self.create('__return(context["foo"])')
        self.assertEqual(42, py(foo=42))

    def test_syntax_error_raises_on_call(self):
        py = self.create('foo(')
        with self.assertRaises(SyntaxError):
            py()

    def test_exceptions_are_propagated(self):
        py = self.create('raise RuntimeError()')
        with self.assertRaises(RuntimeError):
            py()
