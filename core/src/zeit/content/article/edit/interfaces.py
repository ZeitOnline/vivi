# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.article.i18n import MessageFactory as _
import stabledict
import zc.sourcefactory.basic
import zeit.content.image.interfaces
import zeit.edit.interfaces
import zope.schema


class IEditableBody(zeit.edit.interfaces.IArea):
    """Editable representation of an article's body."""


class IParagraph(zeit.edit.interfaces.IBlock):
    """<p/> element."""

    text = zope.schema.Text(title=_('Paragraph-Text'))


class IUnorderedList(IParagraph):
    """<ul/> element."""


class IOrderedList(IParagraph):
    """<ol/> element."""


class IIntertitle(IParagraph):
    """<intertitle/> element."""


class IDivision(zeit.edit.interfaces.IBlock):
    """<division/> element"""

    teaser = zope.schema.TextLine(title=_('Page teaser'))



class ImageLayoutSource(zc.sourcefactory.basic.BasicSourceFactory):
    values = stabledict.StableDict([
        ('small', _('small')),
        ('large', _('large')),
        ('infobox', _('Infobox')),
        ('upright', _('Hochkant')),
        ])

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]


class IImage(zeit.edit.interfaces.IBlock):

    image = zope.schema.Choice(
        title=_("Image"),
        source=zeit.content.image.interfaces.ImageSource())

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=ImageLayoutSource(),
        required=False)
