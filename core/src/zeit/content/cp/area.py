from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
import fractions
import gocept.lxml.interfaces
import grokcore.component as grok
import lxml
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

    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title')

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

    _layout = ObjectPathAttributeProperty(
        '.', 'module')
    _kind = ObjectPathAttributeProperty(
        '.', 'kind')

    supertitle = ObjectPathAttributeProperty(
        '.', 'supertitle')
    title = ObjectPathAttributeProperty(
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

    type = 'area'

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
    def layout(self):
        for layout in zeit.content.cp.interfaces.IArea['layout'].source(self):
            if layout.id == self._layout:
                return layout
        return zeit.content.cp.interfaces.IArea['layout'].default

    @layout.setter
    def layout(self, value):
        self._layout = value.id

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
    # XXX This API is non-obvious: IAutomaticArea also works for areas
    # that are not or can never be automatic.
    for block in zeit.content.cp.interfaces.IAutomaticArea(context).values():
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
