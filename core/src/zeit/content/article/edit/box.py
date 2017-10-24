from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import IBox
import grokcore.component as grok
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.related.related
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zope.component
import zope.interface


class Box(zeit.content.article.edit.block.Block):

    grok.implements(IBox)
    type = 'box'

    supertitle = zeit.cms.content.property.ObjectPathProperty(
        '.supertitle', IBox['supertitle'])

    title = zeit.cms.content.property.ObjectPathProperty(
        '.title', IBox['title'])

    subtitle = zeit.cms.content.property.ObjectPathProperty(
        '.subtitle', IBox['subtitle'])

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'layout',
        zeit.content.article.edit.interfaces.IBox['layout'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Box
    title = _('Box')


class BoxImages(zeit.cms.related.related.RelatedBase):

    zope.component.adapts(IBox)
    zope.interface.implements(zeit.content.image.interfaces.IImages)

    image = zeit.cms.content.reference.SingleResource('.image', 'image')

    fill_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.image', 'fill_color',
        zeit.content.image.interfaces.IImages['fill_color'])
