# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.article.i18n import MessageFactory as _
import zeit.edit.interfaces
import zope.schema


class IEditableBody(zeit.edit.interfaces.IArea):
    """Editable representation of an article's body."""


class IParagraph(zeit.edit.interfaces.IBlock):
    """<p/> element."""

    text = zope.schema.Text(title=_('Paragraph-Text'))
