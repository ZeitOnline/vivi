from zeit.cms.i18n import MessageFactory as _
import collections
import jinja2
import jinja2.utils
import mock
import sys
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.text.interfaces
import zeit.content.text.text
import zope.interface


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


class Environment(jinja2.Environment):
    def handle_exception(self, exc_info=None):
        return rewrite_traceback_stack(exc_info)

def rewrite_traceback_stack(source=None):
    """Rewrite the current exception to replace any tracebacks from
    within compiled template code with tracebacks that look like they
    came from the template source.

    This must be called within an ``except`` block.

    :param exc_info: A :meth:`sys.exc_info` tuple. If not provided,
        the current ``exc_info`` is used.
    :param source: For ``TemplateSyntaxError``, the original source if
        known.
    :return: A :meth:`sys.exc_info` tuple that can be re-raised.
    """

    if source is None:
        source = sys.exc_info()

    exc_type, exc_value, tb = source

    if isinstance(exc_value, jinja2.exceptions.TemplateSyntaxError) and (
            not exc_value.translated):
        exc_value.translated = True
        exc_value.source = source

        try:
            # Remove the old traceback on Python 3, otherwise the frames
            # from the compiler still show up.
            exc_value.with_traceback(None)
        except AttributeError:
            pass

        # Outside of runtime, so the frame isn't executing template
        # code, but it still needs to point at the template.
        tb = fake_traceback(
            exc_value, None, exc_value.filename or "<unknown>", exc_value.lineno
        )
    else:
        # Skip the frame for the render function.
        tb = tb.tb_next

    stack = []

    # Build the stack of traceback object, replacing any in template
    # code with the source file and line information.
    while tb is not None:
        # Skip frames decorated with @internalcode. These are internal
        # calls that aren't useful in template debugging output.
        if tb.tb_frame.f_code in internal_code:
            tb = tb.tb_next
            continue

        template = tb.tb_frame.f_globals.get("__jinja_template__")

        if template is not None:
            lineno = template.get_corresponding_lineno(tb.tb_lineno)
            fake_tb = fake_traceback(exc_value, tb, template.filename, lineno)
            stack.append(fake_tb)
        else:
            stack.append(tb)

        tb = tb.tb_next

    tb_next = None

    # Assign tb_next in reverse to avoid circular references.
    for tb in reversed(stack):
        tb_next = tb_set_next(tb, tb_next)

    return exc_type, exc_value, tb_next


class Template(jinja2.Template):

    jinja2.Template.environment_class = Environment

    def render(self, variables):
        # Patched from upstream to remove any and all dict-wrapping, so we can
        # also pass in a defaultdict to dummy-render a template.
        try:
            return jinja2.utils.concat(
                self.root_render_func(
                    self.new_context(variables, shared=True)))
        except Exception:
            exc_info = sys.exc_info()
        return self.environment.handle_exception(exc_info)


class MockDict(collections.defaultdict):

    def __init__(self):
        super(MockDict, self).__init__(mock.MagicMock)

    def __contains__(self, key):
        return True
