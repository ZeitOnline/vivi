from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.cp.interfaces import IAutomaticTeaserBlock
import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.etree
import lxml.objectify
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.container
import zope.component
import zope.container.interfaces
import zope.interface


class Region(zeit.content.cp.blocks.block.VisibleMixin,
             zeit.edit.container.Base):

    zope.interface.implements(zeit.content.cp.interfaces.IRegion)
    zope.component.adapts(
        zeit.content.cp.interfaces.IBody,
        gocept.lxml.interfaces.IObjectified)

    _find_item = lxml.etree.XPath(
        './*[@area = $name or @cms:__name__ = $name]',
        namespaces=dict(cms='http://namespaces.zeit.de/CMS/cp'))

    type = 'region'

    kind = ObjectPathAttributeProperty('.', 'kind')

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
        keys = []
        for child in xml.getchildren():
            key = child.get('area')
            if key == 'teaser-row-full':
                key = child.get('{http://namespaces.zeit.de/CMS/cp}__name__')
            keys.append(key)
        return keys


class RegionFactory(zeit.edit.block.ElementFactory):

    # XML tags are named "cluster", thus do not change.
    tag_name = 'cluster'
    element_type = 'region'

    def get_xml(self):
        return getattr(lxml.objectify.E, self.tag_name)()


class Area(zeit.content.cp.blocks.block.VisibleMixin,
           zeit.edit.container.TypeOnAttributeContainer):

    zope.interface.implements(zeit.content.cp.interfaces.IArea)
    zope.component.adapts(
        zeit.content.cp.interfaces.IRegion,
        gocept.lxml.interfaces.IObjectified)

    type = 'area'

    _kind = ObjectPathAttributeProperty(
        '.', 'kind')

    supertitle = ObjectPathAttributeProperty(
        '.', 'supertitle')
    _title = ObjectPathAttributeProperty(
        '.', 'title')
    teaserText = ObjectPathAttributeProperty(
        '.', 'teaserText')
    background_color = ObjectPathAttributeProperty(
        '.', 'background_color')

    block_max = ObjectPathAttributeProperty(
        '.', 'block_max', zeit.content.cp.interfaces.IArea['block_max'])
    _overflow_into = ObjectPathAttributeProperty(
        '.', 'overflow_into')

    _apply_teaser_layouts = ObjectPathAttributeProperty(
        '.', 'apply_teaser_layouts',
        zeit.content.cp.interfaces.IArea['apply_teaser_layouts_automatically'])
    _first_teaser_layout = ObjectPathAttributeProperty(
        '.', 'first_teaser_layout')

    _automatic = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic',
        zeit.content.cp.interfaces.IArea['automatic'])

    automatic_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic_type',
        zeit.content.cp.interfaces.IArea['automatic_type'])

    _count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count', zeit.content.cp.interfaces.IArea['count'])

    referenced_cp = zeit.cms.content.property.SingleResource('.referenced_cp')

    hide_dupes = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'hide-dupes', zeit.content.cp.interfaces.IArea[
            'hide_dupes'])

    raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.raw_query', zeit.content.cp.interfaces.IArea['raw_query'])

    MINIMUM_COUNT_TO_REPLACE_DUPLICATES = 5

    def __init__(self, context, xml):
        super(Area, self).__init__(context, xml)
        if 'hide-dupes' not in self.xml.attrib:
            self.hide_dupes = zeit.content.cp.interfaces.IArea[
                'hide_dupes'].default

    @property
    def title(self):
        if self._title:
            return self._title
        if self.referenced_cp is not None:
            return self.referenced_cp.title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def is_teaserbar(self):
        # backward compatibility for teaser bar
        return self.xml.get('area') == 'teaser-row-full'

    @property
    def apply_teaser_layouts_automatically(self):
        """Check if the layout of teaser lists should be set automatically.

        Is used by the event handlers apply_layout_for_added and apply_layout.

        """

        if self._apply_teaser_layouts is not None:
            return self._apply_teaser_layouts

        if self.__name__ != 'lead':
            return False

        cp_type = zeit.content.cp.interfaces.ICenterPage(self).type
        if cp_type in ['archive-print-volume', 'archive-print-year']:
            return False

        if len(list(self.values())) == 0:
            return False

        return True

    @apply_teaser_layouts_automatically.setter
    def apply_teaser_layouts_automatically(self, value):
        self._apply_teaser_layouts = value

    @property
    def first_teaser_layout(self):
        for layout in zeit.content.cp.interfaces.ITeaserBlock['layout'].source(
                self):
            if layout.id == self._first_teaser_layout:
                return layout
        if self.__name__ == 'lead':  # BBB
            return zeit.content.cp.layout.get_layout('leader')
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
            if layout.default:
                return layout
        return None

    @property
    def kind(self):
        # XXX since we hard code the default values for backward compatibility,
        # this also makes it mandatory to have according rules in the kind
        # source definition
        if self.is_teaserbar:
            return 'single'
        if self.__name__ == 'informatives':
            return 'minor'
        if self.__name__ == 'lead':
            return 'major'
        return self._kind or 'single'

    @kind.setter
    def kind(self, value):
        self._kind = value

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
        self._overflow_into = value.__name__

    @property
    def __name__(self):
        name = self.xml.get('area')
        if self.is_teaserbar:
            return self.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')
        return name

    @__name__.setter
    def __name__(self, name):
        if name != self.__name__:
            self._p_changed = True
            if self.is_teaserbar:
                self.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', name)
            self.xml.set('area', name)

    @property
    def automatic(self):
        return self._automatic

    @automatic.setter
    def automatic(self, value):
        if self._automatic and not value:
            self._materialize_filled_values()
        self._automatic = value
        self._fill_with_placeholders()

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value
        self._fill_with_placeholders()

    def _fill_with_placeholders(self):
        if self._automatic:
            for key in self:
                del self[key]
            for i in range(self.count):
                self.create_item('auto-teaser')

    def _materialize_filled_values(self):
        order = self.keys()
        for old in zeit.content.cp.interfaces.IRenderedArea(self).values():
            if not IAutomaticTeaserBlock.providedBy(old):
                continue
            items = list(old)
            new = self.create_item('teaser')
            for content in items:
                new.append(content)
            new.__name__ = old.__name__
            del self[old.__name__]
        # Preserve non-auto blocks.
        self.updateOrder(order)

        # Remove unfilled auto blocks.
        for block in list(self.values()):
            if IAutomaticTeaserBlock.providedBy(block):
                del self[block.__name__]

    @property
    def count_to_replace_duplicates(self):
        return max(self.MINIMUM_COUNT_TO_REPLACE_DUPLICATES, 2 * self.count)

    @property
    def query(self):
        if not hasattr(self.xml, 'query'):
            return ()

        result = []
        for condition in self.xml.query.getchildren():
            channel = unicode(condition)
            subchannel = None
            if ' ' in channel:
                channel, subchannel = channel.split(' ')
            result.append((condition.get('type'), channel, subchannel))
        return tuple(result)

    @query.setter
    def query(self, value):
        try:
            self.xml.remove(self.xml.query)
        except AttributeError:
            pass

        if not value:
            return

        E = lxml.objectify.E
        self.xml.append(E.query(*[E.condition(
            '%s %s' % (channel, subchannel) if subchannel else channel,
            type=type_)
            for type_, channel, subchannel in value]))


class AreaFactory(zeit.edit.block.ElementFactory):

    # XML tags are named "region", thus do not change.
    tag_name = 'region'
    element_type = 'area'
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
@grok.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    if context.automatic and context.automatic_type == 'centerpage':
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
    if (area.block_max is None
            or len(area) <= area.block_max
            or area.overflow_into is None):
        return

    last_block = area.values()[-1]
    del area[last_block.__name__]
    area.overflow_into.insert(0, last_block)
