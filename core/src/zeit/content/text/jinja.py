from zeit.cms.i18n import MessageFactory as _
import collections
import jinja2
import jinja2.utils
import jinja2.debug
import mock
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.text.interfaces
import zeit.content.text.text
import zope.interface
import traceback


@zope.interface.implementer(zeit.content.text.interfaces.IJinjaTemplate)
class JinjaTemplate(zeit.content.text.text.Text):

    title = zeit.cms.content.dav.DAVProperty(
        zeit.content.text.interfaces.IJinjaTemplate['title'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'title')

    def __call__(self, variables, **kw):
        template = Template(self.text, **kw)
        return template.render(variables)


class JinjaTemplateType(zeit.content.text.text.TextType):

    interface = zeit.content.text.interfaces.IJinjaTemplate
    type = 'jinja'
    title = _('Jinja template')
    factory = JinjaTemplate
    addform = zeit.cms.type.SKIP_ADD


class Template(jinja2.Template):

    def render(self, variables):
        # Patched from upstream to remove any and all dict-wrapping, so we can
        # also pass in a defaultdict to dummy-render a template.
        try:
            # Don't use jinja concat function
            # to prevent TypeError if value is None
            return ''.join(str(value) for value in self.root_render_func(
                self.new_context(variables, shared=True)))
        except Exception:
            return ''.join(traceback.format_exception(
                *jinja2.debug.rewrite_traceback_stack()))


class MockDict(collections.defaultdict):

    def __init__(self):
        super(MockDict, self).__init__(mock.MagicMock)

    def __contains__(self, key):
        return True
