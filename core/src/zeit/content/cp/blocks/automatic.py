import gocept.lxml.interfaces
import grokcore.component as grok
import zeit.cms.interfaces
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.component
import zope.interface


# XXX Should we inherit from TeaserBlock?
class AutomaticTeaserBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(
        zeit.content.cp.interfaces.IAutomaticTeaserBlock,
        zope.container.interfaces.IContained)

    zope.component.adapts(
        zeit.content.cp.interfaces.IArea,
        gocept.lxml.interfaces.IObjectified)

    # XXX copy&paste from TeaserBlock
    force_mobile_image = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'force_mobile_image', zeit.content.cp.interfaces.ITeaserBlock[
            'force_mobile_image'])
    text_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'text_color', zeit.content.cp.interfaces.ITeaserBlock[
            'text_color'])
    overlay_level = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'overlay_level', zeit.content.cp.interfaces.ITeaserBlock[
            'overlay_level'])

    volatile = True  # Override to use default=True

    def __init__(self, context, xml):
        super(AutomaticTeaserBlock, self).__init__(context, xml)
        self.entries = []
        self.temporary_layout = None
        # XXX copy&paste from TeaserBlock
        if self.xml.get('module') == 'auto-teaser':
            self.layout = self.layout
        assert self.xml.get('module') != 'auto-teaser'
        if 'text_color' not in self.xml.attrib:
            self.text_color = zeit.content.cp.interfaces.ITeaserBlock[
                'text_color'].default
        if 'overlay_level' not in self.xml.attrib:
            self.overlay_level = zeit.content.cp.interfaces.ITeaserBlock[
                'overlay_level'].default

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)

    def insert(self, index, content):
        self.entries.insert(index, content)

    def __getattr__(self, name):
        if name in zeit.content.cp.interfaces.ITeaserBlock:
            return zeit.content.cp.interfaces.ITeaserBlock[name].default
        raise AttributeError(name)

    def update_topiclinks(self):
        pass

    # XXX copy&paste&tweak from TeaserBlock
    @property
    def layout(self):
        if self.temporary_layout:
            return self.temporary_layout
        id = self.xml.get('module')
        default = zeit.content.cp.layout.NoBlockLayout(self)
        source = zeit.content.cp.interfaces.ITeaserBlock['layout'].source(
            self)
        layout = source.find(id)
        if layout:
            return layout
        for layout in source:
            if layout.is_default(self):
                default = layout
        return default

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


zeit.edit.block.register_element_factory(
    zeit.content.cp.interfaces.IArea, 'auto-teaser')


@grok.adapter(zeit.content.cp.interfaces.IAutomaticTeaserBlock)
@grok.implementer(zeit.cms.interfaces.ICMSContentIterable)
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
