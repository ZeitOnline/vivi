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

    _autopilot = zeit.cms.content.property.ObjectPathProperty('.autopilot')
    _referenced_cp = zeit.cms.content.property.SingleResource('.referenced_cp')
    hide_dupes = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'hide-dupes', zeit.content.cp.interfaces.ITeaserBlock[
            'hide_dupes'])

    display_amount = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'display-amount',
        zeit.content.cp.interfaces.ITeaserBlock['display_amount'])

    AUTOPILOT_ENTRIES = 6

    def __init__(self, context, xml):
        super(TeaserBlock, self).__init__(context, xml)
        if self.xml.get('module') == 'teaser':
            if self.layout is None:
                raise ValueError(_(
                    'No default teaser layout defined for this area.'))
            self.layout = self.layout
        assert self.xml.get('module') != 'teaser'
        if 'hide-dupes' not in self.xml.attrib:
            self.hide_dupes = zeit.content.cp.interfaces.ITeaserBlock[
                'hide_dupes'].default

    def insert(self, index, content):
        self._assert_not_autopilot()
        # self._p_changed = True
        content = zeit.cms.interfaces.ICMSContent(content)
        super(TeaserBlock, self).insert(index, content)

    @property
    def entries(self):
        # overriden so that super.insert() and updateOrder() work
        return self.xml

    def clear(self):
        if not self.autopilot:
            self._p_changed = True
            for entry in self:  # list?
                self.remove(entry)

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

    @property
    def suppress_image_positions(self):
        values = self.xml.get('suppress-image-positions', '').split(',')
        return [int(x) - 1 for x in values if x]

    @suppress_image_positions.setter
    def suppress_image_positions(self, value):
        if not value:
            self.xml.attrib.pop('suppress-image-positions', None)
            return
        self.xml.set('suppress-image-positions', ','.join([
            str(x + 1) for x in value]))

    def __iter__(self):
        if self.autopilot:
            teasers = zeit.content.cp.interfaces.ITeaseredContent(
                self.referenced_cp, iter([]))
            result = []
            for i in range(self.AUTOPILOT_ENTRIES):
                try:
                    result.append(teasers.next())
                except StopIteration:
                    # We've exhausted the available teasers.
                    break
            return iter(result)
        else:
            return super(TeaserBlock, self).__iter__()

    def keys(self):
        if self.autopilot:
            return [c.uniqueId for c in self]
        else:
            return super(TeaserBlock, self).keys()

    def remove(self, *args, **kw):
        self._assert_not_autopilot()
        self._p_changed = True
        super(TeaserBlock, self).remove(*args, **kw)

    def updateOrder(self, *args, **kw):
        self._assert_not_autopilot()
        self._p_changed = True
        super(TeaserBlock, self).updateOrder(*args, **kw)

    def _assert_not_autopilot(self):
        """Ensure that certain methods shall never be called in autopilot."""
        if self.autopilot:
            raise RuntimeError(
                "{cls}: '{method}' is forbidden while on autopilot".format(
                    cls=self, method=sys._getframe(1).f_code.co_name))

    @property
    def autopilot(self):
        return self._autopilot

    @autopilot.setter
    def autopilot(self, autopilot):
        self._p_changed = True
        if autopilot and self.referenced_cp is None:
            raise ValueError(
                'Cannot activate autopilot without referenced centerpage.')
        if autopilot == self._autopilot:
            return
        self._update_autopilot(autopilot)

    @property
    def referenced_cp(self):
        return self._referenced_cp

    @referenced_cp.setter
    def referenced_cp(self, value):
        self._p_changed = True
        self._referenced_cp = value
        if value and zeit.cms.content.interfaces.ICommonMetadata.providedBy(
                value):
            self.title = value.title
            self.read_more = 'mehr %s' % value.title  # XXX i18n?
            self.read_more_url = value.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE, 'http://www.zeit.de/')
        self._update_autopilot(self.autopilot)
        self.update_topiclinks()

    def _update_autopilot(self, autopilot):
        # we need to manipulate self.entries, which is only allowed while not
        # on autopilot. Thus we switch the autopilot mode at different times.
        try:
            include = self.xml[
                '{http://www.w3.org/2003/XInclude}include']
        except AttributeError:
            pass
        else:
            self.xml.remove(include)
        if autopilot:
            self.clear()
            include = zope.component.queryAdapter(
                self.referenced_cp,
                zeit.cms.content.interfaces.IXMLReference,
                name='xi:include')
            if include is not None:
                self.xml.append(include)
            self._autopilot = autopilot
        else:
            self._autopilot = autopilot
            if self.referenced_cp:
                for position, content in enumerate(
                        zeit.content.cp.interfaces.ITeaseredContent(
                            self.referenced_cp)):
                    self.insert(position, content)
                    if position + 1 >= self.AUTOPILOT_ENTRIES:
                        break

    def update_topiclinks(self):
        try:
            self.xml.remove(self.xml.topiclinks)
        except AttributeError:
            pass

        if (self.referenced_cp is None
            or not zeit.content.cp.interfaces.ICenterPage.providedBy(
                self.referenced_cp)):
            return

        self.xml.append(lxml.objectify.E.topiclinks())
        if self.referenced_cp.topiclink_title:
            self.xml.topiclinks.append(
                lxml.objectify.E.title(self.referenced_cp.topiclink_title))
        for i in [1, 2, 3]:
            self._maybe_append_topiclink(
                getattr(self.referenced_cp, 'topiclink_label_%s' % i),
                getattr(self.referenced_cp, 'topiclink_url_%s' % i))

        if not self.xml.topiclinks.getchildren():
            self.xml.remove(self.xml.topiclinks)

    def _maybe_append_topiclink(self, label, url):
        if not url:
            return
        if not label:
            label = url
        self.xml.topiclinks.append(lxml.objectify.E.topiclink(label, href=url))


zeit.edit.block.register_element_factory(
    zeit.content.cp.interfaces.IArea, 'teaser', _('List of teasers'))


@grok.adapter(zeit.content.cp.interfaces.ITeaserBlock)
@grok.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    if context.autopilot:
        yield context.referenced_cp
    for teaser in context:
        yield teaser
        if zeit.content.cp.interfaces.IXMLTeaser.providedBy(teaser):
            yield zeit.cms.interfaces.ICMSContent(teaser.original_uniqueId)


@grok.adapter(zeit.content.cp.interfaces.ICenterPage)
@grok.implementer(zeit.content.cp.interfaces.ITeaseredContent)
def extract_teasers(context):
    for region in context.values():
        for area in region.values():
            for teaser in zeit.content.cp.interfaces.IAutomaticArea(
                    area).values():
                if not zeit.content.cp.interfaces.ITeaserBlock.providedBy(
                        teaser):
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
            if zeit.content.cp.interfaces.IAutomaticArea(area).automatic:
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


@zope.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    zope.container.interfaces.IObjectAddedEvent)
def apply_layout_for_added(context, event):
    """Set layout for new teasers only."""
    area = context.__parent__
    if not area.apply_teaser_layouts_automatically:
        return

    if area.values().index(context) == 0:
        context.layout = area.first_teaser_layout
    else:
        context.layout = area.remaining_teaser_layout


@zope.component.adapter(
    zeit.content.cp.interfaces.IArea,
    zeit.edit.interfaces.IOrderUpdatedEvent)
def apply_layout(context, event):
    """Apply the layout for elements in the teaser list.

    The first one mustn't be small, all other have to be small.
    """
    if not context.apply_teaser_layouts_automatically:
        return

    content = list(context.values())
    first = content[0]
    if (zeit.content.cp.interfaces.ITeaserBlock.providedBy(first) and
            first.layout == context.remaining_teaser_layout):
        first.layout = context.first_teaser_layout

    previously_first = event.old_order[0]
    for elem in content[1:]:
        if not zeit.content.cp.interfaces.ITeaserBlock.providedBy(elem):
            continue
        if elem.__name__ == previously_first:
            elem.layout = context.remaining_teaser_layout


def make_path_for_unique_id(uniqueId):
    return uniqueId.replace(
        zeit.cms.interfaces.ID_NAMESPACE, '/var/cms/work/')


def create_xi_include(context, xpath, name_maker=make_path_for_unique_id):
    include_maker = lxml.objectify.ElementMaker(
        annotate=False,
        namespace='http://www.w3.org/2003/XInclude',
        nsmap={'xi': 'http://www.w3.org/2003/XInclude'},
    )

    path = name_maker(context.uniqueId)

    include = include_maker.include(
        include_maker.fallback('Ziel %s nicht erreichbar.' % context.uniqueId),
        href=path,
        parse='xml',
        xpointer='xpointer(%s)' % xpath)
    return include


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


@zope.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def cp_xi_include(context):
    """Reference a CP as xi:include."""
    include = None
    cp_feed = zope.component.queryAdapter(
        context, zeit.cms.syndication.interfaces.IFeed, name='excerpt')
    if cp_feed is not None:
        include = zope.component.queryAdapter(
            cp_feed, zeit.cms.content.interfaces.IXMLReference,
            name='xi:include')
    if include is None:
        include = create_xi_include(
            context, ("/centerpage/body/cluster[@area='feature']"
                      "/region[@area='lead']/container/block[1]"))
    return include


@zope.component.adapter(zeit.cms.syndication.feed.Feed)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def feed_xi_include(context):
    """Reference a Feed as xi:include.

    Note that this adapts the Feed class instead of the IFeed interface because
    the interface does not guarantee any xml structure.

    """
    return create_xi_include(context, '/channel/container/block')


@grok.subscribe(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_topiclinks_of_referenced_cps(context, event):
    blocks = []
    for region in context.values():
        for area in region.values():
            blocks.extend(area.values())
    for block in blocks:
        if not zeit.content.cp.interfaces.ITeaserBlock.providedBy(
                block):
            continue
        # Note that we can't simply re-set referenced_cp here (as we do
        # with relateds for example), since that might result in different
        # teasers being copied over
        block.update_topiclinks()


@grok.adapter(zeit.content.cp.interfaces.ITeaserBlock)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_teaserblock(context):
    container = getattr(
        lxml.objectify.E, context.xml.tag)(**context.xml.attrib)

    # Render non-content items like topiclinks.
    for child in context.xml.getchildren():
        if child.tag not in [
                'block', '{http://www.w3.org/2003/XInclude}include']:
            container.append(copy.copy(child))

    # Render content.
    for entry in context:
        container.append(zeit.content.cp.interfaces.IRenderedXML(entry))

    return container


@grok.adapter(zeit.cms.interfaces.ICMSContent)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_cmscontent(context):
    block = lxml.objectify.E.block(
        uniqueId=context.uniqueId, href=context.uniqueId)
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(block, suppress_errors=True)
    return block


@grok.adapter(zeit.content.cp.interfaces.IXMLTeaser)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_free_teaser(context):
    block = rendered_xml_cmscontent(context)
    if context.free_teaser:
        block.set('href', context.original_uniqueId)
    return block
