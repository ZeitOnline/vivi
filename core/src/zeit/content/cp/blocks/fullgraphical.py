from zeit.content.cp.i18n import MessageFactory as _
import grokcore.component
import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.interface


class FullGraphicalBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IFullGraphicalBlock)

    referenced_object = zeit.cms.content.property.SingleResource(
        '.block', xml_reference_name='related', attributes=('href',))

    image = zeit.cms.content.property.SingleResource(
        '.image', xml_reference_name='related', attributes=('href',))

    @property
    def layout(self):
        return self.xml.get('layout')

    @layout.setter
    def layout(self, layout):
        if layout != self.layout:
            self._p_changed = True
            self.xml.set('layout', layout)


@grokcore.component.adapter(zeit.content.cp.interfaces.IFullGraphicalBlock)
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    if context.referenced_object is not None:
        yield context.referenced_object
    if context.image is not None:
        yield context.image


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'fullgraphical', _('Fullgraphical Block'))
