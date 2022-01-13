import grokcore.component as grok
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.interfaces


# XXX Should we inherit from TeaserBlock?
@grok.implementer(zeit.content.cp.interfaces.IAutomaticTeaserBlock)
class AutomaticTeaserBlock(zeit.content.cp.blocks.block.Block):

    type = 'auto-teaser'

    # XXX copy&paste from TeaserBlock
    force_mobile_image = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'force_mobile_image', zeit.content.cp.interfaces.ITeaserBlock[
            'force_mobile_image'])

    volatile = True  # Override to use default=True

    def __init__(self, context, xml):
        super(AutomaticTeaserBlock, self).__init__(context, xml)
        self.entries = []
        self.temporary_layout = None
        # XXX copy&paste from TeaserBlock
        if self.xml.get('module') == 'auto-teaser':
            self.layout = self.layout
        assert self.xml.get('module') != 'auto-teaser'

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)

    def insert(self, index, content):
        self.entries.insert(index, content)

    def __getattr__(self, name):
        if name in zeit.content.cp.interfaces.ITeaserBlock:
            return zeit.content.cp.interfaces.ITeaserBlock[name].default
            return zeit.content.cp.interfaces.ITeaserBlock[name].default
        raise AttributeError(name)

    # XXX copy&paste&tweak from TeaserBlock
    @property
    def layout(self):
        if self.temporary_layout:
            return self.temporary_layout
        id = self.xml.get('module')
        source = zeit.content.cp.interfaces.ITeaserBlock['layout'].source(
            self)
        layout = source.find(id)
        if layout:
            return layout
        return zeit.content.cp.interfaces.IArea(self).default_teaser_layout \
            or zeit.content.cp.layout.NoBlockLayout(self)

    @layout.setter
    def layout(self, layout):
        self._p_changed = True
        self.xml.set('module', layout.id)

    def change_layout(self, layout):
        self.temporary_layout = layout

    def materialize(self):
        # Most of this code is quite similar to Area._materialize_auto_blocks,
        # but not similar enough to be extracted.
        area = self.__parent__

        block_id = self.__name__
        rendered = zeit.content.cp.interfaces.IRenderedArea(area)
        for block in rendered.values():
            if block.__name__ == block_id:
                auto_filled = block
                break

        order = area.keys()
        del area[block_id]
        materialized = area.create_item('teaser')
        materialized.update(auto_filled)
        area.updateOrder(order)


class Factory(zeit.content.cp.blocks.block.BlockFactory):

    produces = AutomaticTeaserBlock
    title = None


@grok.adapter(zeit.content.cp.interfaces.IAutomaticTeaserBlock)
@grok.implementer(zeit.edit.interfaces.IElementReferences)
def cms_content_iter(context):
    for teaser in context:
        yield teaser


@grok.adapter(zeit.content.cp.interfaces.IAutomaticTeaserBlock)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    container = zeit.content.cp.blocks.teaser.rendered_xml_teaserblock(context)
    # Change automatic teaser into normal one
    container.attrib['{http://namespaces.zeit.de/CMS/cp}type'] = 'teaser'
    # Make possible change_layout() call take effect.
    container.set('module', context.layout.id)
    return container
