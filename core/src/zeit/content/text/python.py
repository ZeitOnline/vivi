from zeit.cms.i18n import MessageFactory as _
import zeit.cms.type
import zeit.content.text.interfaces
import zeit.content.text.text
import zope.interface


class Break(Exception):
    pass


class PythonScript(zeit.content.text.text.Text):

    zope.interface.implements(zeit.content.text.interfaces.IPythonScript)

    def __call__(self, **kw):
        self._v_result = None
        code = compile(self.text, self.uniqueId, 'exec')
        globs = globals()
        globs['__return'] = self._store_result
        globs['context'] = kw
        try:
            eval(code, globs)
        except Break:
            pass
        return self._v_result

    def _store_result(self, value):
        self._v_result = value
        raise Break()


class PythonScriptType(zeit.content.text.text.TextType):

    interface = zeit.content.text.interfaces.IPythonScript
    type = 'python'
    title = _('Python script')
    factory = PythonScript
    addform = zeit.cms.type.SKIP_ADD
