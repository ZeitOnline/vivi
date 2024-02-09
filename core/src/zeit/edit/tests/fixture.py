import grokcore.component as grok
import zope.interface
import zope.schema

import zeit.cms.interfaces
import zeit.edit.container
import zeit.edit.interfaces


class IContainer(zeit.edit.interfaces.IArea, zeit.edit.interfaces.IBlock):
    pass


class IBlock(zeit.edit.interfaces.IBlock):
    example_amount = zope.schema.Int()

    @zope.interface.invariant
    def check_name_is_not_empty(data):
        if not data.__name__:
            raise zeit.cms.interfaces.ValidationError('The __name__ cannot be empty!')


@grok.implementer(IContainer)
class Container(zeit.edit.container.TypeOnAttributeContainer, grok.MultiAdapter):
    grok.provides(IContainer)
    grok.adapts(IContainer, zeit.cms.interfaces.IXMLElement)
    type = 'container'
    grok.name(type)


class ContainerFactory(zeit.edit.block.TypeOnAttributeElementFactory):
    grok.context(IContainer)
    produces = Container
    title = 'Container'


@grok.implementer(IBlock)
class Block(zeit.edit.block.SimpleElement, grok.MultiAdapter):
    area = IContainer
    grok.provides(IBlock)
    type = 'block'


class BlockFactory(zeit.edit.block.TypeOnAttributeElementFactory):
    grok.context(IContainer)
    produces = Block
    title = 'Block'
