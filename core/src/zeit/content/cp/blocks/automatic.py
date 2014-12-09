import copy
import gocept.lxml.interfaces
import grokcore.component as grok
import lxml
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.component
import zope.interface


class AutomaticTeaserBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(
        zeit.content.cp.interfaces.IAutomaticTeaserBlock,
        zope.container.interfaces.IContained)

    zope.component.adapts(
        zeit.content.cp.interfaces.IArea,
        gocept.lxml.interfaces.IObjectified)

    def __init__(self, context, xml):
        super(AutomaticTeaserBlock, self).__init__(context, xml)
        self.entries = []
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

    # XXX copy&paste from TeaserBlock
    @property
    def layout(self):
        default = None
        for layout in zeit.content.cp.interfaces.ITeaserBlock['layout'].source(
                self):
            if layout.id == self.xml.get('module'):
                return layout
            if layout.default:
                default = layout
        return default

    @layout.setter
    def layout(self, layout):
        self._p_changed = True
        self.xml.set('module', layout.id)


zeit.edit.block.register_element_factory(
    zeit.content.cp.interfaces.IArea, 'auto-teaser')
