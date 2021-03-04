from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.cp.interfaces import IAutomaticTeaserBlock, ITeaserBlock
import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.etree
import lxml.objectify
import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.cp.layout
import zeit.contentquery.helper
import zeit.edit.container
import zeit.edit.interfaces
import zope.component
import zope.container.interfaces
import zope.interface


@zope.component.adapter(
    zeit.content.cp.interfaces.IBody,
    gocept.lxml.interfaces.IObjectified)
@zope.interface.implementer(zeit.content.cp.interfaces.IRegion)
class Region(zeit.content.cp.blocks.block.VisibleMixin,
             zeit.edit.container.Base):

    _find_item = lxml.etree.XPath(
        './*[@area = $name or @cms:__name__ = $name]',
        namespaces=dict(cms='http://namespaces.zeit.de/CMS/cp'))

    type = 'region'

    kind = ObjectPathAttributeProperty('.', 'kind')
    kind_title = ObjectPathAttributeProperty('.', 'kind_title')

    title = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'title')

    @property
    def __name__(self):
        return self.xml.get('area')

    @__name__.setter
    def __name__(self, name):
        if name != self.__name__:
            self._p_changed = True
            self.xml.set('area', name)

    def _get_element_type(self, xml_node):
        return 'area'

    def _get_keys(self, xml):
        return [x.get('area') for x in xml.getchildren()]


class RegionFactory(zeit.edit.block.ElementFactory):

    grok.context(zeit.content.cp.interfaces.IBody)
    produces = Region
    # XML tags are named "cluster", thus do not change.
    tag_name = 'cluster'

    def get_xml(self):
        return getattr(lxml.objectify.E, self.tag_name)()


class ReferencedCpFallbackProperty(
        zeit.cms.content.property.ObjectPathProperty):
    """
    Special ObjectPathProperty which looks up an attribute
    from the referenced cp as a fallback.
    """

    def __get__(self, instance, class_):
        value = super(ReferencedCpFallbackProperty, self).__get__(
            instance, class_)
        if value == self.field.missing_value and instance.referenced_cp:
            value = getattr(instance.referenced_cp,
                            self.field.__name__,
                            self.field.default)
        return value


@zope.component.adapter(
    zeit.content.cp.interfaces.IRegion,
    gocept.lxml.interfaces.IObjectified)
@zope.interface.implementer(zeit.content.cp.interfaces.IArea)
class Area(zeit.content.cp.blocks.block.VisibleMixin,
           zeit.edit.container.TypeOnAttributeContainer):

    type = 'area'
    doc_iface = zeit.content.cp.interfaces.ICenterPage

    automatic_type = zeit.contentquery.helper.AutomaticTypeHelper()
    automatic_type.mapping = {'channel': 'custom'}
    count = zeit.contentquery.helper.CountHelper()
    query = zeit.contentquery.helper.QueryHelper()
    referenced_cp = zeit.contentquery.helper.ReferencedCenterpageHelper()

    kind = ObjectPathAttributeProperty(
        '.', 'kind', zeit.content.cp.interfaces.IArea['kind'],
        use_default=True)

    _layout = ObjectPathAttributeProperty(
        '.', 'module')

    supertitle = ObjectPathAttributeProperty(
        '.', 'supertitle')
    title = ObjectPathAttributeProperty(
        '.', 'title')

    read_more = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'read_more')
    read_more_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'read_more_url')

    _image = zeit.cms.content.property.SingleResource('.image')

    block_max = ObjectPathAttributeProperty(
        '.', 'block_max', zeit.content.cp.interfaces.IArea['block_max'])
    _overflow_into = ObjectPathAttributeProperty(
        '.', 'overflow_into')

    apply_teaser_layouts_automatically = ObjectPathAttributeProperty(
        '.', 'apply_teaser_layouts',
        zeit.content.cp.interfaces.IArea['apply_teaser_layouts_automatically'])
    _first_teaser_layout = ObjectPathAttributeProperty(
        '.', 'first_teaser_layout')

    _automatic = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic',
        zeit.content.cp.interfaces.IArea['automatic'])

    _automatic_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic_type',
        zeit.contentquery.interfaces.IConfiguration['automatic_type'])

    _count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count', zeit.contentquery.interfaces.IConfiguration['count'])

    _referenced_cp = zeit.cms.content.property.SingleResource('.referenced_cp')

    hide_dupes = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'hide-dupes', zeit.contentquery.interfaces.IConfiguration['hide_dupes'],
        use_default=True)

    require_lead_candidates = (
        zeit.cms.content.property.ObjectPathAttributeProperty(
            '.', 'require_lead_candidates',
            zeit.content.cp.interfaces.IArea['require_lead_candidates'],
            use_default=True))

    referenced_topicpage = zeit.cms.content.property.ObjectPathProperty(
        '.referenced_topicpage',
        zeit.contentquery.interfaces.IConfiguration['referenced_topicpage'])
    topicpage_filter = zeit.cms.content.property.ObjectPathProperty(
        '.topicpage_filter',
        zeit.contentquery.interfaces.IConfiguration['topicpage_filter'])

    query_order = zeit.cms.content.property.ObjectPathProperty(
        '.query_order',
        zeit.contentquery.interfaces.IConfiguration['query_order'],
        use_default=True)

    elasticsearch_raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_query',
        zeit.contentquery.interfaces.IConfiguration['elasticsearch_raw_query'])
    elasticsearch_raw_order = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_order',
        zeit.contentquery.interfaces.IConfiguration['elasticsearch_raw_order'],
        use_default=True)
    is_complete_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_complete_query',
        zeit.contentquery.interfaces.IConfiguration['is_complete_query'],
        use_default=True)

    rss_feed = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty('.', 'rss_feed'),
        zeit.contentquery.interfaces.IConfiguration['rss_feed'])

    topiclink_label_1 = ReferencedCpFallbackProperty(
        '.topiclink_label_1',
        zeit.content.cp.interfaces.IArea['topiclink_label_1'])

    topiclink_url_1 = ReferencedCpFallbackProperty(
        '.topiclink_url_1',
        zeit.content.cp.interfaces.IArea['topiclink_url_1'])

    topiclink_label_2 = ReferencedCpFallbackProperty(
        '.topiclink_label_2',
        zeit.content.cp.interfaces.IArea['topiclink_label_2'])

    topiclink_url_2 = ReferencedCpFallbackProperty(
        '.topiclink_url_2',
        zeit.content.cp.interfaces.IArea['topiclink_url_2'])

    topiclink_label_3 = ReferencedCpFallbackProperty(
        '.topiclink_label_3',
        zeit.content.cp.interfaces.IArea['topiclink_label_3'])

    topiclink_url_3 = ReferencedCpFallbackProperty(
        '.topiclink_url_3',
        zeit.content.cp.interfaces.IArea['topiclink_url_3'])

    area_color_theme = (
        zeit.cms.content.property.ObjectPathAttributeProperty(
            '.', 'area_color_theme'))

    @property
    def image(self):
        if self._image:
            return self._image
        if self.referenced_cp is not None:
            images = zeit.content.image.interfaces.IImages(
                self.referenced_cp, None)
            if images is None:
                return None
            return images.image

    @image.setter
    def image(self, value):
        self._image = value

    @property
    def first_teaser_layout(self):
        for layout in zeit.content.cp.interfaces.ITeaserBlock['layout'].source(
                self):
            if layout.id == self._first_teaser_layout:
                return layout
        return None

    @first_teaser_layout.setter
    def first_teaser_layout(self, value):
        if value is None:
            self._first_teaser_layout = None
        else:
            self._first_teaser_layout = value.id

    @property
    def default_teaser_layout(self):
        for layout in zeit.content.cp.interfaces.ITeaserBlock['layout'].source(
                self):
            if layout.is_default(self):
                return layout
        return None

    @property
    def kind_title(self):
        """Retrieve title for this kind of Area from XML config."""
        area_config = zeit.content.cp.layout.AREA_CONFIGS(None).find(self.kind)
        if area_config:
            return area_config.title

    @property
    def overflow_into(self):
        if self._overflow_into is None:
            return None
        return zeit.content.cp.interfaces.ICenterPage(self).get_recursive(
            self._overflow_into)

    @overflow_into.setter
    def overflow_into(self, value):
        if value is None:
            self._overflow_into = None
        else:
            candidates = zeit.content.cp.interfaces.IArea[
                'overflow_into'].source(self)
            if value not in candidates:
                self._overflow_into = None
            else:
                self._overflow_into = value.__name__

    @property
    def __name__(self):
        return self.xml.get('area')

    @__name__.setter
    def __name__(self, name):
        if name != self.__name__:
            self._p_changed = True
            self.xml.set('area', name)

    @property
    def automatic(self):
        return self._automatic

    @automatic.setter
    def automatic(self, value):
        if self.automatic and not value:
            self._materialize_auto_blocks()
        self._automatic = value
        if value:
            self._create_auto_blocks()

    def count_helper_tasks(self):
        self.adjust_auto_blocks_to_count()

    def adjust_auto_blocks_to_count(self):
        """Does not touch any block that is not an IAutomaticTeaserBlock, so
        only the number of _automatic_ teasers is configured via the
        `Area.count` setting. Thus we may contain more than `Area.count`
        teasers.
        """
        if not self.automatic:
            return

        # We want the configured blocks here, not the rendered ones.
        filter_values = super(Area, self).filter_values

        to_adjust = len(list(filter_values(ITeaserBlock))) - (self.count or 0)
        if to_adjust == 0:
            return

        changed = 0
        if to_adjust > 0:
            automatic_blocks = list(filter_values(IAutomaticTeaserBlock))
            while changed < to_adjust and automatic_blocks:
                changed += 1
                block = automatic_blocks.pop(-1)
                del self[block.__name__]
        elif to_adjust < 0:
            to_adjust = abs(to_adjust)
            while changed < to_adjust:
                changed += 1
                self.create_item('auto-teaser')

    def _create_auto_blocks(self):
        """Add automatic teaser blocks so we have #count of them.
        We _replace_ previously materialized ones, preserving their #layout
        (copying it to the auto block at the same position).

        """
        self.adjust_auto_blocks_to_count()

        order = self.keys()
        for block in self.values():
            if not block.volatile:
                continue

            auto_block = self.create_item('auto-teaser')
            auto_block.__name__ = block.__name__  # required to updateOrder

            if ITeaserBlock.providedBy(block):
                auto_block.layout = block.layout

            # Only deletes first occurrence of __name__, i.e. `block`
            del self[block.__name__]

        # Preserve order of blocks that are kept when turning AutoPilot on.
        self.updateOrder(order)

    def _materialize_auto_blocks(self):
        """Replace automatic teaser blocks by teaser blocks with same content
        and same attributes (e.g. `layout`).

        (Make sure this method only runs when #automatic is enabled, otherwise
        IRenderedArea will not retrieve results from the content query source.)

        """
        order = self.keys()
        for old in zeit.content.cp.interfaces.IRenderedArea(self).values():
            if not IAutomaticTeaserBlock.providedBy(old):
                continue

            # Delete automatic teaser first, since adding normal teaser will
            # delete the last automatic teaser via the
            # `adjust_auto_blocks_to_count` event handler.
            # (Deleting doesn't remove __name__ or __parent__, so we can still
            # copy those afterwards)
            del self[old.__name__]

            new = self.create_item('teaser')
            new.update(old)

        # Preserve order of non-auto blocks.
        self.updateOrder(order)

        # Remove unfilled auto blocks.
        for block in list(self.values()):
            if IAutomaticTeaserBlock.providedBy(block):
                del self[block.__name__]

    def filter_values(self, *interfaces):
        return zeit.content.cp.interfaces.IRenderedArea(self).filter_values(
            *interfaces)


class AreaFactory(zeit.edit.block.ElementFactory):

    grok.context(zeit.content.cp.interfaces.IRegion)
    produces = Area
    # XML tags are named "region", thus do not change.
    tag_name = 'region'
    title = _('Area')

    def get_xml(self):
        return getattr(lxml.objectify.E, self.tag_name)()


@grok.adapter(zeit.content.cp.interfaces.IElement)
@grok.implementer(zeit.content.cp.interfaces.IRegion)
def element_to_region(context):
    return zeit.content.cp.interfaces.IRegion(context.__parent__, None)


@grok.adapter(zeit.content.cp.interfaces.IElement)
@grok.implementer(zeit.content.cp.interfaces.IArea)
def element_to_area(context):
    return zeit.content.cp.interfaces.IArea(context.__parent__, None)


@grok.adapter(zeit.content.cp.interfaces.IRegion)
@grok.implementer(zeit.edit.interfaces.IArea)
def region_to_area(context):
    """A region *contains*, areas."""
    return None


@grok.adapter(zeit.content.cp.interfaces.IArea)
@grok.implementer(zeit.edit.interfaces.IElementReferences)
def cms_content_iter(context):
    if (context.automatic and
            context.automatic_type == 'centerpage' and
            context.referenced_cp is not None):
        yield context.referenced_cp
    for content in zeit.content.cp.centerpage.cms_content_iter(
            zeit.content.cp.interfaces.IRenderedArea(context)):
        yield content


@grok.adapter(zeit.content.cp.interfaces.IRegion)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_mosaic(context):
    root = getattr(lxml.objectify.E, context.xml.tag)(**context.xml.attrib)
    for item in context.values():
        root.append(zeit.content.cp.interfaces.IRenderedXML(item))
    return root


@grok.adapter(zeit.content.cp.interfaces.IArea)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    area = getattr(lxml.objectify.E, context.xml.tag)(**context.xml.attrib)
    area.attrib.pop('automatic', None)
    for block in zeit.content.cp.interfaces.IRenderedArea(context).values():
        area.append(zeit.content.cp.interfaces.IRenderedXML(block))
    return area


@grok.subscribe(
    zeit.content.cp.interfaces.IBlock,
    zope.container.interfaces.IObjectAddedEvent)
def overflow_blocks(context, event):
    area = context.__parent__
    if (area.automatic or
            area.block_max is None or
            len(area) <= area.block_max or
            area.overflow_into is None):
        return

    last_block = area.values()[-1]
    del area[last_block.__name__]
    area.overflow_into.insert(0, last_block)
    overflow_blocks(last_block, None)


@grok.subscribe(
    zeit.content.cp.interfaces.IBlock,
    zope.container.interfaces.IObjectMovedEvent)
def adjust_auto_blocks_to_count(context, event):
    if IAutomaticTeaserBlock.providedBy(context):
        return  # avoid infty loop when adding / deleting auto teaser
    area = context.__parent__
    area.adjust_auto_blocks_to_count()


@grok.subscribe(
    zeit.content.cp.interfaces.IArea,
    zope.container.interfaces.IObjectMovedEvent)
def maybe_remove_overflow(context, event):
    # We only want add or move, but not remove.
    if zope.lifecycleevent.IObjectRemovedEvent.providedBy(event):
        return

    # Check overflow from context.
    context.overflow_into = context.overflow_into

    # Check overflow to context.
    cp = zeit.content.cp.interfaces.ICenterPage(context)
    # Looking at *all* areas may include some that cannot have been affected
    # by this move, but determining those is more trouble than it's worth.
    for region in cp.values():
        for area in region.values():
            if area.overflow_into == context:
                area.overflow_into = area.overflow_into


@grok.subscribe(
    zeit.content.cp.interfaces.IRegion,
    zeit.edit.interfaces.IOrderUpdatedEvent)
def maybe_remove_overflow_after_sort(context, event):
    for area in context.values():
        area.overflow_into = area.overflow_into


@grok.subscribe(
    zeit.content.cp.interfaces.IArea,
    zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def overflow_excessive_blocks(context, event):
    for description in event.descriptions:
        if description.interface is zeit.content.cp.interfaces.IArea:
            if 'block_max' in description.attributes:
                while len(context) > context.block_max:
                    last_block = context.values()[-1]
                    overflow_blocks(last_block, None)


@grok.subscribe(
    zeit.content.cp.interfaces.IArea,
    zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def prefill_metadata_from_referenced_cp(context, event):
    for description in event.descriptions:
        if description.interface is zeit.content.cp.interfaces.IArea:
            if 'referenced_cp' not in description.attributes:
                return
    if context.referenced_cp is None:
        return

    for field in ['title', 'supertitle']:
        if getattr(context, field):
            continue
        setattr(context, field, getattr(context.referenced_cp, field))

    if not context.read_more_url:
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        live_prefix = config['live-prefix']
        context.read_more_url = context.referenced_cp.uniqueId.replace(
            zeit.cms.interfaces.ID_NAMESPACE,
            live_prefix)
