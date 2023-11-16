from zeit.cms.i18n import MessageFactory as _
import zeit.cms.type
import zeit.content.text.interfaces
import zeit.content.text.text
import zope.interface


class Break(Exception):
    pass


class EvalExecHelper:
    def _globals(self, globs):
        globs['__return'] = self._store_result
        return globs

    def _store_result(self, value):
        """We want to support multiple statements with a return value.
        Since `eval` only offers a choice between "simple expression" or
        "statements, but without any return value", we use the latter and
        provide our own "`return` function" that stores the result and then
        raises an exception (which we catch and ignore) so the execution flow
        stops there (just like normal `return` behaves).
        """
        self._v_result = value
        raise Break()


@zope.interface.implementer(zeit.content.text.interfaces.IPythonScript)
class PythonScript(zeit.content.text.text.Text, EvalExecHelper):
    def __call__(self, **kw):
        self._v_result = None
        code = compile(self.text, filename=self.uniqueId, mode='exec')
        globs = self._globals(globals())
        globs['context'] = kw
        try:
            eval(code, globs)  # noqa
        except Break:
            pass
        return self._v_result


class PythonScriptType(zeit.content.text.text.TextType):
    interface = zeit.content.text.interfaces.IPythonScript
    type = 'python'
    title = _('Python script')
    factory = PythonScript
    addform = zeit.cms.type.SKIP_ADD
