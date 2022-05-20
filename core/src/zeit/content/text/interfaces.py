from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.contentsource
import zeit.cms.repository.interfaces
import zope.schema


DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/text'


class CannotEncode(zope.schema.ValidationError):

    def doc(self):
        text, encoding, e = self.args
        return _('Could not encode charachters ${start}-${end} to ${encoding} '
                 '(${characters}): ${reason}',
                 mapping=dict(
                     start=e.start,
                     end=e.end,
                     encoding=encoding,
                     characters=text[e.start:e.end],
                     reason=e.reason))

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.args[2])


class Code(zope.schema.Text):
    pass


class IText(zeit.cms.repository.interfaces.IDAVContent):
    """A simple object containing unparsed text."""

    text = Code(
        title=_('Content'))

    encoding = zope.schema.Choice(
        title=_('Encoding'),
        values=('UTF-8', 'ISO8859-15'),
        default='UTF-8')

    mimeType = zeit.cms.repository.interfaces.IFile['mimeType'].bind(object())
    mimeType.default = 'text/plain'

    @zope.interface.invariant
    def text_encodable(data):
        if data.text:
            try:
                data.text.encode(data.encoding)
            except UnicodeEncodeError as e:
                raise CannotEncode(data.text, data.encoding, e)

        return True


class TextSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'zeit.content.text'
    check_interfaces = (IText,)


textSource = TextSource()


class IPythonScript(IText):

    def __call__(**kw):
        """Evaluates the python code and returns the result.

        Due to Python mechanics, code needs to use ``__return(value)`` instead
        of the normal ``return value`` to return a result.

        The keyword arguments are provided to the code in a dict named
        ``context``.
        """


class IJinjaTemplate(IText):

    title = zope.schema.TextLine(title=_("Title"))

    def __call__(**kw):
        """Renders the content as a jina template and returns the result.

        The keyword arguments are provided to the template.
        """


class JSON(zope.schema.Text):
    pass


class IJSON(IText):

    text = JSON(title=_('Content'))

    mimeType = zeit.cms.repository.interfaces.IFile['mimeType'].bind(object())
    mimeType.default = 'application/json'


class IValidationSchema(zope.interface.Interface):

    schema_url = zope.schema.TextLine(
        title=_('url of schema'),
        required=False)

    field_name = zope.schema.TextLine(
        title=_('specific schema to use for validation'),
        required=False)

    def _get(self, context):
        """
        Get yaml schema to validate json from url
        """

    def validate_context(self, context):
        """
        Validate JSON data against schema
        """


class SchemaValidationError(Exception):
    pass


class IEmbed(IText):

    render_as_template = zope.schema.Bool(title=_("Render as template?"))

    parameter_definition = Code(
        title=_("Parameter definition"),
        required=False)

    parameter_fields = zope.interface.Attribute('dict of schema fields')

    vivi_css = Code(
        title=_("Embed CSS"),
        required=False)

    amp_code = Code(
        title=_("Embed AMP Code"),
        description=_("Please use an AMP validator to check your code"),
        required=False)


class EmbedSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'zeit.content.text.embed'
    check_interfaces = (IText, IEmbed)


embedSource = EmbedSource()
