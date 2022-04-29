import copy
import grokcore.component as grok
import zeit.cms.content.property
import zeit.content.cp.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component
import zope.interface


@zope.component.adapter(zeit.content.cp.interfaces.IElement)
@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
def centerpage_for_element(context):
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__, None)


@zope.component.adapter(zeit.edit.interfaces.IElement)
@zope.interface.implementer(zeit.edit.interfaces.IElementReferences)
def cms_content_iter(context):
    return iter([])


class VisibleMixin:

    visible = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'visible', zeit.content.cp.interfaces.IElement[
            'visible'])

    visible_mobile = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'visible_mobile', zeit.content.cp.interfaces.IElement[
            'visible_mobile'])

    def __init__(self, context, xml):
        super(VisibleMixin, self).__init__(context, xml)
        if 'visible' not in self.xml.attrib:
            self.visible = zeit.content.cp.interfaces.IElement[
                'visible'].default
        if 'visible_mobile' not in self.xml.attrib:
            self.visible_mobile = zeit.content.cp.interfaces.IElement[
                'visible_mobile'].default


class Block(VisibleMixin, zeit.edit.block.SimpleElement):

    grok.baseclass()
    area = zeit.content.cp.interfaces.IArea

    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle')
    supertitle_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle_url')

    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title')

    volatile = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'volatile',
        zeit.content.cp.interfaces.IBlock['volatile'],
        use_default=True)

    # XXX Is this attribute used anywhere? Imho it's dead code.
    publisher = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'publisher')
    publisher_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'publisher_url')

    read_more = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'read_more')
    read_more_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'read_more_url')

    background_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'background_color')

    @property
    def type_title(self):
        """Retrieve title for this block type from XML config."""
        module_config = zeit.content.cp.layout.MODULE_CONFIGS(None).find(
            self.type)
        if module_config:
            return module_config.title


class BlockFactory(zeit.edit.block.TypeOnAttributeElementFactory):

    grok.baseclass()
    grok.context(zeit.content.cp.interfaces.IArea)


@grok.adapter(zeit.content.cp.interfaces.IBlock)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    return copy.copy(context.xml)


@zope.interface.implementer(zeit.content.cp.interfaces.IUnknownBlock)
class UnknownBlock(Block, zeit.edit.block.UnknownBlock):

    area = zeit.content.cp.interfaces.IArea
