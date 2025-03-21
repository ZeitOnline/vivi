from unittest import mock
import collections

from jinja2.runtime import Undefined
import jinja2
import jinja2.utils
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.text.interfaces
import zeit.content.text.text


@zope.interface.implementer(zeit.content.text.interfaces.IJinjaTemplate)
class JinjaTemplate(zeit.content.text.text.Text):
    title = zeit.cms.content.dav.DAVProperty(
        zeit.content.text.interfaces.IJinjaTemplate['title'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'title',
    )

    channels = zeit.cms.content.dav.DAVProperty(
        zeit.content.text.interfaces.IJinjaTemplate['channels'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'channels',
        use_default=True,
    )

    def __call__(self, variables, **kw):
        patch = None
        if kw.pop('output_format', None) == 'json':
            # Kludgy way to make jinja autoescape work for JSON instead of HTML
            # XXX This is not threadsafe! We should probably look into a more
            # stable solution, like https://github.com/pallets/jinja/issues/503
            kw['autoescape'] = True
            patch = mock.patch('jinja2.runtime.escape', new=json_escape)
            patch.start()
        template = Template(self.text, **kw)
        result = template.render(variables)
        if patch:
            patch.stop()
        return result


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
            return jinja2.utils.concat(
                self.root_render_func(self.new_context(variables, shared=True))
            )
        except Exception:
            self.environment.handle_exception()


class MockDict(collections.defaultdict):
    def __init__(self):
        super().__init__(mock.MagicMock)

    def __contains__(self, key):
        return True


def json_escape(value):
    # type Markup inherits from str
    # but Markup.replace escapes the replacement arguments!
    if type(value) is str:  # noqa: E721
        return value.replace('"', r'\"')
    elif isinstance(value, Undefined):
        return ''
    else:
        return value
