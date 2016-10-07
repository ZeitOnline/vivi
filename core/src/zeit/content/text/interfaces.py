from zeit.cms.i18n import MessageFactory as _
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


class IText(zeit.cms.repository.interfaces.IDAVContent):
    """A simple object containing unparsed text."""

    text = zope.schema.Text(
        title=_('Content'))

    encoding = zope.schema.Choice(
        title=_('Encoding'),
        values=('UTF-8', 'ISO8859-15'),
        default='UTF-8')

    @zope.interface.invariant
    def text_encodable(data):
        if data.text:
            try:
                data.text.encode(data.encoding)
            except UnicodeEncodeError, e:
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
