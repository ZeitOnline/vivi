# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


class Liveblog(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.ILiveblog)
    type = 'liveblog'

    blog_id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'blogID',
        zeit.content.article.edit.interfaces.ILiveblog['blog_id'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Liveblog
    title = _('Liveblog')
