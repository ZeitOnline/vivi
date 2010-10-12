# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zeit.edit.interfaces


class Division(zeit.edit.block.Element,
                grokcore.component.MultiAdapter):

    grokcore.component.adapts(
      zeit.content.article.edit.interfaces.IEditableBody,
      gocept.lxml.interfaces.IObjectified)
    grokcore.component.name('division')
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IDivision)
    grokcore.component.provides(
        zeit.content.article.edit.interfaces.IDivision)

    type = 'division'

    # TODO: set xml attribute type="page"

    teaser = zeit.cms.content.property.ObjectPathAttributeProperty(
      '.', 'teaser', zeit.content.article.edit.interfaces.IDivision['teaser'])
