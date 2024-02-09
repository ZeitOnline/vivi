import grokcore.component as grok
import lxml.builder
import lxml.etree
import zope.component
import zope.interface
import zope.lifecycleevent

from zeit.cms.content.cache import cached_on_content, content_cache
from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.cp.interfaces import IAutomaticTeaserBlock, ICenterPage, ITeaserBlock
import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.cp.layout
import zeit.contentquery.configuration
import zeit.contentquery.interfaces
import zeit.edit.container
import zeit.edit.interfaces


@zope.component.adapter(zeit.content.cp.interfaces.IBody, zeit.cms.interfaces.IXMLElement)
@zope.interface.implementer(zeit.content.cp.interfaces.IRegion)
class Region(zeit.content.cp.blocks.block.VisibleMixin, zeit.edit.container.Base):
    _find_item = lxml.etree.XPath(
        './*[@area = $name or @cms:__name__ = $name]',
        namespaces={'cms': 'http://namespaces.zeit.de/CMS/cp'},
    )

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
        return getattr(lxml.builder.E, self.tag_name)()


class ReferencedCpFallbackProperty(zeit.cms.content.property.ObjectPathProperty):
    """
    Special ObjectPathProperty which looks up an attribute
    from the referenced cp as a fallback.
    """

    def __get__(self, instance, class_):
        value = super().__get__(instance, class_)
        if value == self.field.missing_value and instance.referenced_cp:
            value = getattr(instance.referenced_cp, self.field.__name__, self.field.default)
        return value


@zope.component.adapter(zeit.content.cp.interfaces.IRegion, zeit.cms.interfaces.IXMLElement)
@zope.interface.implementer(zeit.content.cp.interfaces.IArea)
class Area(
    zeit.content.cp.blocks.block.VisibleMixin,
    zeit.edit.container.TypeOnAttributeContainer,
    zeit.contentquery.configuration.Configuration,
):
    type = 'area'

    kind = ObjectPathAttributeProperty(
        '.', 'kind', zeit.content.cp.interfaces.IArea['kind'], use_default=True
    )

    _layout = ObjectPathAttributeProperty('.', 'module')

    supertitle = ObjectPathAttributeProperty('.', 'supertitle')
    title = ObjectPathAttributeProperty('.', 'title')

    read_more = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'read_more')
    read_more_url = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'read_more_url')

    _image = zeit.cms.content.property.SingleResource('.image')

    apply_teaser_layouts_automatically = ObjectPathAttributeProperty(
        '.',
        'apply_teaser_layouts',
        zeit.content.cp.interfaces.IArea['apply_teaser_layouts_automatically'],
    )
    _first_teaser_layout = ObjectPathAttributeProperty('.', 'first_teaser_layout')

    _automatic = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic', zeit.content.cp.interfaces.IArea['automatic']
    )

    _automatic_type_bbb = {'channel': 'custom'}
    _automatic_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic_type', zeit.content.cp.interfaces.IArea['automatic_type']
    )

    query = zeit.contentquery.configuration.CustomQueryProperty({'Channel': 'channels'})

    _count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count', zeit.content.cp.interfaces.IArea['count']
    )

    topiclink_label_1 = ReferencedCpFallbackProperty(
        '.topiclink_label_1', zeit.content.cp.interfaces.IArea['topiclink_label_1']
    )

    topiclink_url_1 = ReferencedCpFallbackProperty(
        '.topiclink_url_1', zeit.content.cp.interfaces.IArea['topiclink_url_1']
    )

    topiclink_label_2 = ReferencedCpFallbackProperty(
        '.topiclink_label_2', zeit.content.cp.interfaces.IArea['topiclink_label_2']
    )

    topiclink_url_2 = ReferencedCpFallbackProperty(
        '.topiclink_url_2', zeit.content.cp.interfaces.IArea['topiclink_url_2']
    )

    topiclink_label_3 = ReferencedCpFallbackProperty(
        '.topiclink_label_3', zeit.content.cp.interfaces.IArea['topiclink_label_3']
    )

    topiclink_url_3 = ReferencedCpFallbackProperty(
        '.topiclink_url_3', zeit.content.cp.interfaces.IArea['topiclink_url_3']
    )

    background_color = ObjectPathAttributeProperty('.', 'background_color')

    @property
    def image(self):
        if self._image:
            return self._image
        if self.referenced_cp is None:
            return None
        images = zeit.content.image.interfaces.IImages(self.referenced_cp, None)
        if images is None:
            return None
        return images.image

    @image.setter
    def image(self, value):
        self._image = value

    @property
    def first_teaser_layout(self):
        for layout in zeit.content.cp.interfaces.ITeaserBlock['layout'].source(self):
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
        for layout in zeit.content.cp.interfaces.ITeaserBlock['layout'].source(self):
            if layout.is_default(self):
                return layout
        return None

    @property
    def kind_title(self):
        """Retrieve title for this kind of Area from XML config."""
        area_config = zeit.content.cp.layout.AREA_CONFIGS(None).find(self.kind)
        if area_config:
            return area_config.title
        return None

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

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value
        self.adjust_auto_blocks_to_count()

    @property
    def referenced_cp(self):
        return self._referenced_cp

    @referenced_cp.setter
    def referenced_cp(self, value):
        self.check_for_self_reference(value)
        self._referenced_cp = value

    def check_for_self_reference(self, value):
        # It is still possible to build larger circles (e.g A->C->A)
        # but a sane user should not ignore the errormessage shown in the
        # cp-editor and preview.
        # Checking for larger circles is not reasonable here.
        ref = zeit.content.cp.interfaces.ICenterPage
        if value.uniqueId == ref(self).uniqueId:
            raise ValueError("A centerpage can't reference itself!")

    def adjust_auto_blocks_to_count(self):
        """Does not touch any block that is not an IAutomaticTeaserBlock, so
        only the number of _automatic_ teasers is configured via the
        `Area.count` setting. Thus we may contain more than `Area.count`
        teasers.
        """
        if not self.automatic:
            return

        # We want the configured blocks here, not the rendered ones.
        filter_values = super().filter_values

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

    @property
    @cached_on_content(keyfunc=lambda x: x.__name__)
    def existing_teasers(self):
        current_area = self
        cp = ICenterPage(self)
        area_teasered_content = content_cache(cp, 'area_teasered_content')
        area_manual_content = content_cache(cp, 'area_manual_content')

        seen = set()
        above = True
        for area in cp.cached_areas:
            if area == current_area:
                above = False
            if not area.consider_for_dupes:
                continue
            if above:  # automatic teasers above current area
                if area not in area_teasered_content:
                    area_teasered_content[area] = set(
                        zeit.content.cp.interfaces.ITeaseredContent(area)
                    )

                seen.update(area_teasered_content[area])
            else:  # manual teasers below (or in) current area
                if area not in area_manual_content:
                    # Probably not worth a separate adapter (like
                    # ITeaseredContent), since the use case is pretty
                    # specialised.
                    area_manual_content[area] = set(
                        zeit.content.cp.blocks.teaser.extract_manual_teasers(area)
                    )
                seen.update(area_manual_content[area])
        return seen

    def filter_values(self, *interfaces):
        return zeit.content.cp.interfaces.IRenderedArea(self).filter_values(*interfaces)


class AreaFactory(zeit.edit.block.ElementFactory):
    grok.context(zeit.content.cp.interfaces.IRegion)
    produces = Area
    # XML tags are named "region", thus do not change.
    tag_name = 'region'
    title = _('Area')

    def get_xml(self):
        return getattr(lxml.builder.E, self.tag_name)()


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
    if (
        context.automatic
        and context.automatic_type == 'centerpage'
        and context.referenced_cp is not None
    ):
        yield context.referenced_cp
    for content in zeit.content.cp.centerpage.cms_content_iter(
        zeit.content.cp.interfaces.IRenderedArea(context)
    ):
        yield content


@grok.adapter(zeit.content.cp.interfaces.IRegion)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml_mosaic(context):
    root = getattr(lxml.builder.E, context.xml.tag)(**context.xml.attrib)
    for item in context.values():
        root.append(zeit.content.cp.interfaces.IRenderedXML(item))
    return root


@grok.adapter(zeit.content.cp.interfaces.IArea)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    area = getattr(lxml.builder.E, context.xml.tag)(**context.xml.attrib)
    area.attrib.pop('automatic', None)
    for block in zeit.content.cp.interfaces.IRenderedArea(context).values():
        area.append(zeit.content.cp.interfaces.IRenderedXML(block))
    return area


@grok.subscribe(zeit.content.cp.interfaces.IBlock, zope.lifecycleevent.IObjectMovedEvent)
def adjust_auto_blocks_to_count(context, event):
    if IAutomaticTeaserBlock.providedBy(context):
        return  # avoid infty loop when adding / deleting auto teaser
    area = context.__parent__
    area.adjust_auto_blocks_to_count()


@grok.subscribe(zeit.content.cp.interfaces.IArea, zope.lifecycleevent.IObjectModifiedEvent)
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
            zeit.cms.interfaces.ID_NAMESPACE, live_prefix
        )
