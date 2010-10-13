# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import zeit.edit.block
import zeit.edit.interfaces


class BlockFactory(zeit.edit.block.ElementFactory,
                   grokcore.component.Adapter):

    grokcore.component.baseclass()
    grokcore.component.implements(zeit.edit.interfaces.IElementFactory)
    grokcore.component.context(
        zeit.content.article.edit.interfaces.IEditableBody)
