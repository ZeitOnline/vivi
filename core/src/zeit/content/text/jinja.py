from zeit.cms.i18n import MessageFactory as _
import jinja2
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.text.interfaces
import zeit.content.text.text
import zope.interface


class JinjaTemplate(zeit.content.text.text.Text):

    zope.interface.implements(zeit.content.text.interfaces.IJinjaTemplate)

    title = zeit.cms.content.dav.DAVProperty(
        zeit.content.text.interfaces.IJinjaTemplate['title'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'title')

    def __call__(self, **kw):
        template = jinja2.Template(self.text)
        return template.render(**kw)


class JinjaTemplateType(zeit.content.text.text.TextType):

    interface = zeit.content.text.interfaces.IJinjaTemplate
    type = 'jinja'
    title = _('Jinja template')
    factory = JinjaTemplate
    addform = zeit.cms.type.SKIP_ADD
