from zeit.cms.i18n import MessageFactory as _
import collections  # noqa make available to eval()
import logging
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.content.modules.interfaces
import zeit.content.text.interfaces
import zeit.content.text.python
import zeit.content.text.text
import zope.interface
import zope.schema  # noqa make available to eval()


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.content.text.interfaces.IEmbed)
class Embed(zeit.content.text.text.Text,
            zeit.content.text.python.EvalExecHelper):

    zeit.cms.content.dav.mapProperties(
        zeit.content.text.interfaces.IEmbed,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('render_as_template', 'parameter_definition', 'vivi_css'))

    @property
    def parameter_fields(self):
        try:
            code = self.parameter_definition or '__return({})'
            if '__return' not in code:
                code = '__return(%s)' % code
            # XXX Cases like `zope.schema.Choice(source=zeit.content.image
            # .interfaces.imageSource)` currently work only accidentally, since
            # everything we need apparently is imported elsewhere already.
            code = compile(code, filename=self.uniqueId, mode='exec')
            try:
                fields = eval(code, self._globals(globals()))
            except zeit.content.text.python.Break:
                fields = self._v_result
        except Exception:
            log.warning(
                'Parameter definition of %s had errors, treated as empty',
                self.uniqueId, exc_info=True)
            return {}
        if not isinstance(fields, dict):
            log.warning(
                'Parameter definition of %s is not a dict, treated as empty',
                self.uniqueId)
            return {}

        invalid = []
        for name, field in fields.items():
            if not zope.schema.interfaces.IField.providedBy(field):
                log.warning(
                    'Parameter definition %s of %s is not a field, ignored',
                    name, self.uniqueId)
                invalid.append(name)
                continue
            if not field.title:
                field.title = str(name).title()
            field.__name__ = name
            # Slight circular dependency
            field.interface = zeit.content.modules.interfaces.IEmbedParameters

        for name in invalid:
            del fields[name]

        return fields


class EmbedType(zeit.content.text.text.TextType):

    interface = zeit.content.text.interfaces.IEmbed
    type = 'embed'
    title = _('Embed')
    factory = Embed
    addform = 'zeit.content.text.embed.Add'
    addpermission = 'zeit.content.text.AddEmbed'
