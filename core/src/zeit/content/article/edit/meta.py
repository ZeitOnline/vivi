# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component.meta
import martian
import zeit.content.article.edit.block
import zope.component


class BlockFactoryGrokker(martian.ClassGrokker):

    martian.component(zeit.content.article.edit.block.BlockFactory)
    martian.directive(grokcore.component.context,
                      get_default=grokcore.component.meta.default_context)

    def execute(self, factory, config, context, **kw):
        name = factory.element_type = factory.produces.type
        provides = zeit.edit.interfaces.IElementFactory
        config.action(
            discriminator=('adapter', context, provides, name),
            callable=zope.component.provideAdapter,
            args=(factory, (context,), provides, name),
            )
        return True
