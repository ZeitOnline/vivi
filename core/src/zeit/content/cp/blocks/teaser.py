from zeit.content.cp.i18n import MessageFactory as _
import copy
import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.objectify
import sys
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.syndication.feed
import zeit.cms.syndication.interfaces
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.container.contained
import zope.container.interfaces
import zope.copypastemove.interfaces
import zope.interface
import zope.lifecycleevent
import zope.schema


CP_FEED_NAME = '%s.lead'


class ColumnSpec(zeit.cms.content.xmlsupport.Persistent):

    zope.interface.implements(zeit.content.cp.interfaces.ITeaserBlockColumns)
    zope.component.adapts(zeit.content.cp.interfaces.ITeaserBlock)

    column_1 = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'column_1', zope.schema.Int())

    def __init__(self, block):
        self.xml = block.xml
        self.context = block
        self.__parent__ = block

    def _get_columns(self):
        teasers = len(self.context)
        if len(self) == 1:
            return (teasers,)
        if self.column_1 is None or teasers < self.column_1:
            left = teasers
            right = 0
        else:
            left = min(self.column_1, teasers)
            right = teasers - self.column_1
        return left, right

    def __getitem__(self, idx):
        try:
            return self._get_columns()[idx]
        except IndexError:
            raise IndexError('column index out of range')

    def __setitem__(self, idx, value):
        if idx != 0:
            raise KeyError('Can only set column 0')
        self.column_1 = value

    def __len__(self):
        columns = self.context.layout.columns
        assert columns in (1, 2)
        return columns

    def __repr__(self):
        spec = ', '.join(str(x) for x in self._get_columns())
        return 'ColumnSpec(%s)' % spec


class TeaserBlock(
        zeit.content.cp.blocks.block.Block,
        zeit.cms.syndication.feed.Feed):

    # TeaserBlock reuses Feed for its "list of IElement" behaviour

    zope.interface.implementsOnly(
        zeit.content.cp.interfaces.ITeaserBlock,
        zeit.cms.syndication.interfaces.IFeed,
        zope.container.interfaces.IContained)

    zope.component.adapts(
        zeit.content.cp.interfaces.IArea,
        gocept.lxml.interfaces.IObjectified)

    def __init__(self, context, xml):
        super(TeaserBlock, self).__init__(context, xml)
        if self.xml.get('module') == 'teaser':
            if self.layout is None:
                raise ValueError(_(
                    'No default teaser layout defined for this area.'))
            self.layout = self.layout
        assert self.xml.get('module') != 'teaser'

    @property
    def entries(self):
        # overriden so that super.insert() and updateOrder() work
        return self.xml

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
    zeit.content.cp.interfaces.IArea, 'teaser', _('List of teasers'))


@grok.adapter(zeit.content.cp.interfaces.ITeaserBlock)
@grok.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    for teaser in context:
        yield teaser
        if zeit.content.cp.interfaces.IXMLTeaser.providedBy(teaser):
            yield zeit.cms.interfaces.ICMSContent(teaser.original_uniqueId)


@grok.adapter(zeit.content.cp.interfaces.ICenterPage)
@grok.implementer(zeit.content.cp.interfaces.ITeaseredContent)
def extract_teasers_from_cp(context):
    for region in context.values():
        for area in region.values():
            for teaser in zeit.content.cp.interfaces.ITeaseredContent(area):
                yield teaser


@grok.adapter(zeit.content.cp.interfaces.IArea)
@grok.implementer(zeit.content.cp.interfaces.ITeaseredContent)
def extract_teasers_from_area(context):
    for teaser in zeit.content.cp.interfaces.IRenderedArea(context).values():
        if not zeit.content.cp.interfaces.ITeaserBlock.providedBy(teaser):
            continue
        for content in list(teaser):
            yield content


def extract_manual_teasers(context):
    for teaser in context.values():
        if not zeit.content.cp.interfaces.ITeaserBlock.providedBy(teaser):
            continue
        for content in list(teaser):
            yield content


# XXX Does anyone actually use this, pulling an IFeed into a CP via autopilot?
@grok.adapter(zeit.cms.syndication.interfaces.IFeed)
@grok.implementer(zeit.content.cp.interfaces.ITeaseredContent)
def extract_teasers(context):
    return iter(context)


def cp_feed_name(name):
    return CP_FEED_NAME % name


@grok.subscribe(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def create_cp_channel(context, event):
    feed = zeit.cms.syndication.feed.Feed()
    teasers = zeit.content.cp.interfaces.ITeaseredContent(context)
    for i, obj in enumerate(teasers):
        if zeit.cms.interfaces.ICMSContent.providedBy(obj):
            feed.insert(i, obj)
    feed_name = cp_feed_name(context.__name__)
    if automatic_enabled(context):
        feed.xml.set('automatic', 'True')
    context.__parent__[feed_name] = feed


def automatic_enabled(centerpage):
    for region in centerpage.values():
        for area in region.values():
            if area.automatic:
                return True
    return False


@grok.subscribe(
    zeit.content.cp.interfaces.ITeaserBlock,
    zope.container.interfaces.IObjectMovedEvent)
def change_layout_if_not_allowed_in_new_area(context, event):
    # Getting a default layout can mean that the current layout is not allowed
    # in this area (can happen when a block was moved between areas). Thus, we
    # want to change the XML to actually reflect the new default layout.
    if context.layout.default:
        context.layout = context.layout


@grok.subscribe(
    zeit.content.cp.interfaces.ITeaserBlock,
    zope.container.interfaces.IObjectAddedEvent)
def apply_layout_for_added(context, event):
    """Set layout for new teasers only."""
    area = context.__parent__
    if not area.apply_teaser_layouts_automatically:
        return

    # XXX The overflow_blocks handler also listens to the IObjectAddedEvent and
    # may have removed this item from the container. Since overflow_blocks
    # retrieves the item via a getitem access, it is newly created from the XML
    # node. That means `context is not context.__parent__[context.__name__]`.
    # Since it is not the same object, changes to the newly created object will
    # not be reflected in the context given to event handlers. So we need a
    # guard here to check if overflow_blocks has removed the item and skip the
    # method in case it has. (Modifying __parent__ of context does not seem
    # like a good idea, hell might break loose. So lets just forget about this
    # possiblity.)
    if context.__name__ not in area.keys():
        return

    if area.keys().index(context.__name__) == 0:
        context.layout = area.first_teaser_layout
    else:
        context.layout = area.default_teaser_layout


@grok.subscribe(
    zeit.content.cp.interfaces.IArea,
    zeit.edit.interfaces.IOrderUpdatedEvent)
def set_layout_to_default_when_moved_down_from_first_position(area, event):
    if not area.apply_teaser_layouts_automatically:
        return

    # XXX The overflow_blocks handler listens to the IObjectAddedEvent and may
    # have removed this item from the container. In that case we have to do
    # nothing, since checking the layout is handled by the new container.
    if event.old_order[0] not in area.keys():
        return

    previously_first = area[event.old_order[0]]
    if (zeit.content.cp.interfaces.ITeaserBlock.providedBy(previously_first)
            and area.values().index(previously_first)) > 0:
        previously_first.layout = area.default_teaser_layout


@grok.adapter(zeit.content.cp.interfaces.ICenterPage, name='excerpt')
@grok.implementer(zeit.cms.syndication.interfaces.IFeed)
def feed_excerpt(context):
    return zeit.cms.interfaces.ICMSContent(
        cp_feed_name(context.uniqueId), None)


class ExcerptDependency(object):

    zope.component.adapts(zeit.content.cp.interfaces.ICenterPage)
    zope.interface.implements(
        zeit.workflow.interfaces.IPublicationDependencies)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        cp_feed = zope.component.queryAdapter(
            self.context, zeit.cms.syndication.interfaces.IFeed,
            name='excerpt')
        if cp_feed is None:
            return []
        return [cp_feed]


@grok.adapter(zeit.content.cp.interfaces.ITeaserBlock)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_teaserblock(context):
    container = getattr(
        lxml.objectify.E, context.xml.tag)(**context.xml.attrib)

    # Render non-content items like topiclinks.
    for child in context.xml.getchildren():
        # BBB: xinclude is not generated anymore, but some might still exist.
        if child.tag not in [
                'block', '{http://www.w3.org/2003/XInclude}include']:
            container.append(copy.copy(child))

    # Render content.
    for entry in context:
        container.append(zope.component.getAdapter(
            entry, zeit.content.cp.interfaces.IRenderedXML, name="content"))

    return container


@grok.adapter(zeit.cms.interfaces.ICMSContent, name="content")
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_cmscontent(context):
    block = lxml.objectify.E.block(
        uniqueId=context.uniqueId, href=context.uniqueId)
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(block, suppress_errors=True)
    return block


@grok.adapter(zeit.content.cp.interfaces.IXMLTeaser, name="content")
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_free_teaser(context):
    block = rendered_xml_cmscontent(context)
    if context.free_teaser:
        block.set('href', context.original_uniqueId)
    return block
