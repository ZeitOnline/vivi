# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import gocept.lxml.interfaces
import grokcore.component
import lxml.objectify
import rwproperty
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
import zope.container.interfaces
import zope.copypastemove.interfaces
import zope.interface
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


class TeaserBlock(zeit.content.cp.blocks.block.Block,
                  zeit.cms.syndication.feed.Feed):

    # TeaserBlock reuses Feed for its "list of IElement" behaviour

    zope.interface.implementsOnly(
        zeit.content.cp.interfaces.ITeaserBlock,
        zeit.cms.syndication.interfaces.IFeed,
        zope.container.interfaces.IContained)

    zope.component.adapts(
        zeit.content.cp.interfaces.ILead,
        gocept.lxml.interfaces.IObjectified)

    def __init__(self, context, xml):
        super(TeaserBlock, self).__init__(context, xml)
        if self.xml.get('module') == 'teaser':
            self.layout = self.layout
        assert self.xml.get('module') != 'teaser'

    def insert(self, index, content):
        content = zeit.cms.interfaces.ICMSContent(content)
        if zeit.content.cp.teasergroup.interfaces.ITeaserGroup.providedBy(
            content):
            self._insert_teaser_group(index, content)
        else:
            self._insert_content(index, content)

    def _insert_teaser_group(self, index, group):
        for i, content in enumerate(group.teasers):
            if zeit.content.cp.interfaces.ITeaser.providedBy(content):
                # Teaser objects referenced in teaser groups are copied.
                copier = zope.copypastemove.interfaces.IObjectCopier(content)
                copied_name = copier.copyTo(content.__parent__)
                content = content.__parent__[copied_name]
            self._insert_content(index+i, content)

    def _insert_content(self, index, content):
        super(TeaserBlock, self).insert(index, content)

    @property
    def entries(self):
        # overriden so that super.insert() and updateOrder() work
        return self.xml

    def clear(self):
        self._p_changed = True
        for entry in self:
            self.remove(entry)

    @rwproperty.getproperty
    def layout(self):
        default = None
        for layout in zeit.content.cp.interfaces.ITeaserBlock['layout'].source(
            self):
            if layout.id == self.xml.get('module'):
                return layout
            if layout.default:
                default = layout
        return default

    @rwproperty.setproperty
    def layout(self, layout):
        self._p_changed = True
        self.xml.set('module', layout.id)


class AutoPilotTeaserBlock(TeaserBlock):

    zope.interface.implementsOnly(
        zeit.content.cp.interfaces.IAutoPilotTeaserBlock,
        zeit.cms.syndication.interfaces.IFeed,
        zope.container.interfaces.IContained)

    zope.component.adapts(
        zeit.content.cp.interfaces.IRegion,
        gocept.lxml.interfaces.IObjectified)

    _autopilot = zeit.cms.content.property.ObjectPathProperty('.autopilot')
    _referenced_cp = zeit.cms.content.property.SingleResource('.referenced_cp')
    hide_dupes = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'hide-dupes', zeit.content.cp.interfaces.IAutoPilotTeaserBlock[
        'hide_dupes'])

    AUTOPILOT_ENTRIES = 6

    def __init__(self, *args, **kw):
        super(AutoPilotTeaserBlock, self).__init__(*args, **kw)
        if 'hide-dupes' not in self.xml.attrib:
            self.hide_dupes = zeit.content.cp.interfaces.IAutoPilotTeaserBlock[
                'hide_dupes'].default

    def __iter__(self):
        if self.autopilot:
            feed = zeit.cms.syndication.interfaces.IReadFeed(
                self.referenced_cp, [])
            return iter(list(feed)[:self.AUTOPILOT_ENTRIES])
        else:
            return super(AutoPilotTeaserBlock, self).__iter__()

    def keys(self):
        if self.autopilot:
            return [c.uniqueId for c in self]
        else:
            return super(AutoPilotTeaserBlock, self).keys()

    def insert(self, *args, **kw):
        self._p_changed = True
        self._forbidden_on_autopilot('insert', *args, **kw)

    def remove(self, *args, **kw):
        self._p_changed = True
        self._forbidden_on_autopilot('remove', *args, **kw)

    def updateOrder(self, *args, **kw):
        self._p_changed = True
        self._forbidden_on_autopilot('updateOrder', *args, **kw)

    def _forbidden_on_autopilot(self, method, *args, **kw):
        if self.autopilot:
            raise RuntimeError("%s: '%s' is forbidden while on autopilot"
                               % (self, method))
        else:
            return getattr(super(AutoPilotTeaserBlock, self), method)(*args,
                                                                      **kw)

    @rwproperty.getproperty
    def autopilot(self):
        return self._autopilot

    @rwproperty.setproperty
    def autopilot(self, autopilot):
        self._p_changed = True
        if autopilot and self.referenced_cp is None:
            raise ValueError(
                'Cannot activate autopilot without referenced centerpage.')
        if autopilot == self._autopilot:
            return
        self._update_autopilot(autopilot)

    @rwproperty.getproperty
    def referenced_cp(self):
        return self._referenced_cp

    @rwproperty.setproperty
    def referenced_cp(self, value):
        self._p_changed = True
        self._referenced_cp = value
        self._update_autopilot(self.autopilot)

    def clear(self):
        if not self.autopilot:
            for entry in list(self):
                self.remove(entry)

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
                    zeit.cms.syndication.interfaces.IReadFeed(
                        self.referenced_cp)):
                    self.insert(position, content)
                    if position + 1 >= self.AUTOPILOT_ENTRIES:
                        break


zeit.edit.block.register_element_factory(
    zeit.content.cp.interfaces.IRegion, 'teaser', _('List of teasers'))


@grokcore.component.adapter(zeit.content.cp.interfaces.ITeaserBlock)
@grokcore.component.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    for teaser in context:
        yield teaser
        if zeit.content.cp.interfaces.IXMLTeaser.providedBy(teaser):
            yield zeit.cms.interfaces.ICMSContent(teaser.original_uniqueId)


@grokcore.component.adapter(zeit.content.cp.interfaces.IAutoPilotTeaserBlock)
@grokcore.component.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def autopilot_cms_content_iter(context):
    if context.autopilot:
        yield context.referenced_cp
    for obj in cms_content_iter(context):
        yield obj


class CenterpageFeed(zeit.cms.syndication.feed.Feed):
    """A centerpage can be interpreted as a feed."""

    zope.component.adapts(zeit.content.cp.interfaces.ICenterPage)
    zope.interface.implementsOnly(zeit.cms.syndication.interfaces.IReadFeed)

    def __init__(self, context):
        self.context = context

    @property
    def xml(self):
        return self.context.xml

    def iterentries(self):
        return self.xml.xpath("/centerpage/body/cluster[@area='feature']"
                              "/region[@area='lead']/container/block[1]")


def cp_feed_name(name):
    return CP_FEED_NAME % name


@grokcore.component.subscribe(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def create_cp_channel(context, event):
    feed = zeit.cms.syndication.feed.Feed()
    cp_feed = zeit.cms.syndication.interfaces.IReadFeed(context)
    for obj in reversed(list(cp_feed)):
        if zeit.cms.interfaces.ICMSContent.providedBy(obj):
            feed.insert(0, obj)
    feed_name = cp_feed_name(context.__name__)
    context.__parent__[feed_name] = feed


@zope.component.adapter(
    zeit.edit.interfaces.IElement,
    zope.container.interfaces.IObjectAddedEvent)
def apply_layout_for_added(context, event):
    region = context.__parent__
    # Are we leaders?
    if zeit.content.cp.interfaces.ILead.providedBy(region):
        apply_layout(region, None)


@zope.component.adapter(
    zeit.content.cp.interfaces.ILead,
    zope.lifecycleevent.IObjectModifiedEvent)
def apply_layout(context, event):
    """Apply the layout for elements in the teaser list.

    The first one mustn't be small, all other have to be small.
    """
    cp_type = zeit.content.cp.interfaces.ICenterPage(context).type
    if (cp_type == 'archive-print-volume') or (cp_type == 'archive-print-year'):
        return
    # We are leaders!
    content = list(context.values())
    if len(content) == 0:
        return
    first = content[0]
    buttons = zeit.content.cp.layout.get_layout('buttons')
    if (zeit.content.cp.interfaces.ITeaserBlock.providedBy(first) and
        (first.layout == buttons or first.layout is None)):
        first.layout = zeit.content.cp.layout.get_layout('leader')
    for elem in content[1:]:
        if not zeit.content.cp.interfaces.ITeaserBlock.providedBy(elem):
            continue
        if elem.layout is None:
            elem.layout = buttons


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


@grokcore.component.adapter(zeit.content.cp.interfaces.ICenterPage,
                            name='excerpt')
@grokcore.component.implementer(zeit.cms.syndication.interfaces.IFeed)
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
            self.context, zeit.cms.syndication.interfaces.IFeed, name='excerpt')
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
