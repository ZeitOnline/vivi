import gocept.lxml.interfaces
import grokcore.component as grok
import zeit.cms.interfaces
import zeit.edit.container
import zeit.edit.interfaces
import zope.interface


class IContainer(zeit.edit.interfaces.IArea,
                 zeit.edit.interfaces.IBlock):
    pass


class IBlock(zeit.edit.interfaces.IBlock):

    @zope.interface.invariant
    def check_name_is_not_empty(data):
        if not data.__name__:
            raise zeit.cms.interfaces.ValidationError(
                'The __name__ cannot be empty!')


class Container(zeit.edit.container.TypeOnAttributeContainer,
                grok.MultiAdapter):

    grok.implements(IContainer)
    grok.provides(IContainer)
    grok.adapts(
        IContainer,
        gocept.lxml.interfaces.IObjectified)
    grok.name('container')

zeit.edit.block.register_element_factory(IContainer, 'container', 'Container')


class Block(zeit.edit.block.SimpleElement, grok.MultiAdapter):

    area = IContainer
    grok.implements(IBlock)
    grok.provides(IBlock)
    type = 'block'

zeit.edit.block.register_element_factory(IContainer, 'block', 'Block')
