import copy

import grokcore.component as grok
import lxml.builder
import zope.component
import zope.interface
import zope.lifecycleevent
import zope.location.interfaces
import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.content.cp.blocks.block
import zeit.content.cp.feed
import zeit.content.cp.interfaces
import zeit.content.gallery.interfaces
import zeit.edit.interfaces


class Layoutable:
    def __init__(self, context, xml):
        super().__init__(context, xml)
        if self.xml.get('module') == self.type:
            if isinstance(self.layout, zeit.content.cp.layout.NoBlockLayout):
                raise ValueError(_('No default teaser layout defined for this area.'))
            self.layout = self.layout
        assert self.xml.get('module') != self.type

    @property
    def layout(self):
        id = self.xml.get('module')
        source = zeit.content.cp.interfaces.ITeaserBlock['layout'].source(self)
        layout = source.find(id)
        if layout:
            return layout
        return zeit.content.cp.interfaces.IArea(
            self
        ).default_teaser_layout or zeit.content.cp.layout.NoBlockLayout(self)

    @layout.setter
    def layout(self, layout):
        self._p_changed = True
        self.xml.set('module', layout.id)


@zope.interface.implementer_only(
    zeit.content.cp.interfaces.ITeaserBlock,
    zeit.content.cp.interfaces.IFeed,
    zope.location.interfaces.IContained,
)
class TeaserBlock(Layoutable, zeit.content.cp.blocks.block.Block, zeit.content.cp.feed.ContentList):
    type = 'teaser'

    force_mobile_image = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.',
        'force_mobile_image',
        zeit.content.cp.interfaces.ITeaserBlock['force_mobile_image'],
        use_default=True,
    )

    @property
    def entries(self):
        # overriden so that super.insert() and updateOrder() work
        return self.xml

    @property
    def references(self):
        try:
            return next(iter(self))
        except StopIteration:
            return None

    @references.setter
    def references(self, value):
        for key in self.keys():
            self._remove_by_id(key)
        if value is not None:
            self.append(value)

    TEASERBLOCK_FIELDS = (
        set(zope.schema.getFieldNames(zeit.content.cp.interfaces.ITeaserBlock))
        - set(zeit.cms.content.interfaces.IXMLRepresentation)
        - {'references'}
    )

    def update(self, other):
        if not zeit.content.cp.interfaces.ITeaserBlock.providedBy(other):
            raise ValueError('%r is not an ITeaserBlock' % other)
        # Copy teaser contents.
        for content in other:
            self.append(content)
        # Copy block properties (including __name__ and __parent__)
        for name in self.TEASERBLOCK_FIELDS:
            setattr(self, name, getattr(other, name))


class Factory(zeit.content.cp.blocks.block.BlockFactory):
    produces = TeaserBlock
    title = _('List of teasers')


@grok.adapter(zeit.content.cp.interfaces.IArea, zeit.cms.interfaces.ICMSContent, int)
@grok.implementer(zeit.edit.interfaces.IElement)
def make_block_from_content(container, content, position):
    block = Factory(container)(position)
    block.insert(0, content)
    return block


@grok.adapter(zeit.content.cp.interfaces.ITeaserBlock)
@grok.implementer(zeit.edit.interfaces.IElementReferences)
def cms_content_iter(context):
    for teaser in context:
        yield teaser


@grok.adapter(zeit.content.cp.interfaces.ICenterPage)
@grok.implementer(zeit.content.cp.interfaces.ITeaseredContent)
def extract_teasers_from_cp(context):
    for region in context.body.values():
        for area in region.values():
            for teaser in zeit.content.cp.interfaces.ITeaseredContent(area):
                yield teaser


@grok.adapter(zeit.content.cp.interfaces.IArea)
@grok.implementer(zeit.content.cp.interfaces.ITeaseredContent)
def extract_teasers_from_area(context):
    for teaser in context.filter_values(zeit.content.cp.interfaces.ITeaserBlock):
        for content in list(teaser):
            yield content


def extract_manual_teasers(context):
    for teaser in context.values():
        if not zeit.content.cp.interfaces.ITeaserBlock.providedBy(teaser):
            continue
        for content in list(teaser):
            yield content


@grok.subscribe(zeit.content.cp.interfaces.ITeaserBlock, zope.lifecycleevent.IObjectMovedEvent)
def change_layout_if_not_allowed_in_new_area(context, event):
    # Getting a default layout can mean that the current layout is not allowed
    # in this area (can happen when a block was moved between areas). Thus, we
    # want to change the XML to actually reflect the new default layout.
    if context.layout.is_default(context):
        context.layout = context.layout


@grok.subscribe(zeit.content.cp.interfaces.ITeaserBlock, zope.lifecycleevent.IObjectAddedEvent)
def apply_layout_for_added(context, event):
    """Set layout for new teasers only."""
    area = context.__parent__
    if not area.apply_teaser_layouts_automatically:
        return

    if area.keys().index(context.__name__) == 0:
        context.layout = area.first_teaser_layout
    else:
        context.layout = area.default_teaser_layout


@grok.subscribe(zeit.content.cp.interfaces.IArea, zeit.edit.interfaces.IOrderUpdatedEvent)
def set_layout_to_default_when_moved_down_from_first_position(area, event):
    if not area.apply_teaser_layouts_automatically:
        return

    previously_first = area[event.old_order[0]]
    if (
        zeit.content.cp.interfaces.ITeaserBlock.providedBy(previously_first)
        and area.values().index(previously_first)
    ) > 0:
        previously_first.layout = area.default_teaser_layout


@grok.adapter(zeit.content.cp.interfaces.ITeaserBlock)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_teaserblock(context):
    container = getattr(lxml.builder.E, context.xml.tag)(**context.xml.attrib)

    # Render non-content items like topiclinks.
    for child in context.xml.getchildren():
        # BBB: xinclude is not generated anymore, but some might still exist.
        if child.tag not in ['block', '{http://www.w3.org/2003/XInclude}include']:
            container.append(copy.copy(child))

    # Render content.
    for entry in context:
        node = zope.component.queryAdapter(
            entry, zeit.content.cp.interfaces.IRenderedXML, name='content'
        )
        if node is not None:
            container.append(node)

    return container


@grok.adapter(zeit.cms.interfaces.ICMSContent, name='content')
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_cmscontent(context):
    if not context.uniqueId:
        return None
    block = lxml.builder.E.block(uniqueId=context.uniqueId, href=context.uniqueId)
    return block
