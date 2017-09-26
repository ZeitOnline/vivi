from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import IBox

import grokcore.component as grok
import zeit.cms.related.related
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zeit.edit.block
import zope.component
import zope.interface


class Box(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IArticleArea
    grok.implements(IBox)
    type = 'box'

    teaserSupertitle = zeit.cms.content.property.ObjectPathProperty(
        '.supertitle', IBox['teaserSupertitle'])

    teaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.title', IBox['teaserTitle'])

    teaserText = zeit.cms.content.property.ObjectPathProperty(
        '.text', IBox['teaserText'])

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
