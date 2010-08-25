# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

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
