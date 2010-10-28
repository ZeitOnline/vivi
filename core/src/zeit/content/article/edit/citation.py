# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


class Citation(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.ICitation)
    type = 'citation'

    text  = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'text', zeit.content.article.edit.interfaces.ICitation['text'])
    text_2  = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'text2', zeit.content.article.edit.interfaces.ICitation['text_2'])
    attribution = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'attribution',
        zeit.content.article.edit.interfaces.ICitation['attribution'])
    attribution_2 = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'attribution2',
        zeit.content.article.edit.interfaces.ICitation['attribution_2'])
    url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'url',
        zeit.content.article.edit.interfaces.ICitation['url'])
    url_2 = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'url2',
        zeit.content.article.edit.interfaces.ICitation['url_2'])
    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'layout',
        zeit.content.article.edit.interfaces.ICitation['layout'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Citation
    title = _('Citation')
