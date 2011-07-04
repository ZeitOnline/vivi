# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component as grok
import zeit.cms.testing
import zeit.edit.container
import zeit.edit.interfaces


EditLayer = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = EditLayer


class IContainer(zeit.edit.interfaces.IArea,
                 zeit.edit.interfaces.IBlock):
    pass


class IBlock(zeit.edit.interfaces.IBlock):
    pass


class Container(zeit.edit.container.TypeOnAttributeContainer,
                grok.MultiAdapter):

    grok.implements(IContainer)
    grok.provides(IContainer)
    grok.adapts(
        IContainer,
        gocept.lxml.interfaces.IObjectified)
    grok.name('container')

zeit.edit.block.register_element_factory(IContainer, 'container', 'Container')


class Block(zeit.edit.block.SimpleElement):

    area = IContainer
    grok.implements(IBlock)
    type = 'block'

zeit.edit.block.register_element_factory(IContainer, 'block', 'Block')
