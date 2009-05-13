# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import lxml.objectify
import rwproperty
import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.cms.syndication.feed
import zeit.cms.syndication.interfaces
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.component
import zope.container.contained
import zope.container.interfaces
import zope.interface


class TeaserBlock(zeit.content.cp.blocks.block.Block,
                 zeit.cms.syndication.feed.Feed):

    # TeaserBlock reuses Feed for its "list of ICMSContent" behaviour

    zope.interface.implementsOnly(
        zeit.content.cp.interfaces.ITeaserBlock,
        zeit.cms.syndication.interfaces.IFeed,
        zope.container.interfaces.IContained)

    _autopilot = zeit.cms.content.property.ObjectPathProperty('.autopilot')
    referenced_cp = zeit.cms.content.property.SingleResource('.referenced_cp')

    @property
    def entries(self):
        # overriden so that super.insert() and updateOrder() work
        return self.xml

    def iterentries(self):
        if self.autopilot:
            feed = zeit.cms.syndication.interfaces.IReadFeed(
                self.referenced_cp)
            return iter(feed)
        else:
            return super(TeaserBlock, self).iterentries()

    def keys(self):
        if self.autopilot:
            return [c.uniqueId for c in self.iterentries()]
        else:
            return super(TeaserBlock, self).keys()

    def insert(self, *args, **kw):
        self._forbidden_on_autopilot('insert', *args, **kw)

    def remove(self, *args, **kw):
        self._forbidden_on_autopilot('remove', *args, **kw)

    def updateOrder(self, *args, **kw):
        self._forbidden_on_autopilot('updateOrder', *args, **kw)

    def _forbidden_on_autopilot(self, method, *args, **kw):
        if self.autopilot:
            raise RuntimeError("%s: '%s' is forbidden while on autopilot"
                               % (self, method))
        else:
            return getattr(super(TeaserBlock, self), method)(*args, **kw)

    @rwproperty.getproperty
    def autopilot(self):
        return self._autopilot

    @rwproperty.setproperty
    def autopilot(self, autopilot):
        if autopilot and self.referenced_cp is None:
            raise ValueError(
                'Cannot activate autopilot without referenced centerpage.')
        if autopilot == self._autopilot:
            return

        # we need to manipulate self.entries, which is only allowed while not
        # on autopilot. Thus we switch the autopilot mode at different times.
        if autopilot:
            self.clear()
            self.xml.append(
                zope.component.getAdapter(
                    self.referenced_cp,
                    zeit.cms.content.interfaces.IXMLReference,
                    name='xi:include'))
            self._autopilot = autopilot
        else:
            self._autopilot = autopilot
            try:
                include = self.xml[
                    '{http://www.w3.org/2003/XInclude}include']
            except AttributeError:
                pass
            else:
                self.xml.remove(include)
            if self.referenced_cp:
                for position, content in enumerate(
                    zeit.cms.syndication.interfaces.IReadFeed(
                        self.referenced_cp)):
                    self.insert(position, content)

    def clear(self):
        if not self.autopilot:
            for entry in self:
                self.remove(entry)

    @rwproperty.getproperty
    def layout(self):
        for layout in zeit.content.cp.interfaces.ITeaserBlock['layout'].source(
            self):
            if layout.id == self.xml.get('module'):
                return layout
        return zeit.content.cp.interfaces.IReadTeaserBlock[
            'layout'].missing_value

    @rwproperty.setproperty
    def layout(self, layout):
        self.xml.set('module', layout.id)


TeaserBlockFactory = zeit.content.cp.blocks.block.blockFactoryFactory(
    zeit.content.cp.interfaces.IRegion,
    TeaserBlock, 'teaser', _('List of teasers'))


@zope.component.adapter(zeit.content.cp.interfaces.ITeaserBlock)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    for teaser in context:
        yield teaser



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


@zope.component.adapter(
    zeit.content.cp.interfaces.IBlock,
    zope.container.contained.IObjectAddedEvent)
def apply_layout_for_added(context, event):
    region = context.__parent__
    # Are we leaders?
    if zeit.content.cp.interfaces.ILeadRegion.providedBy(region):
        apply_layout(region, None)


@zope.component.adapter(
    zeit.content.cp.interfaces.ILeadRegion,
    zope.lifecycleevent.IObjectModifiedEvent)
def apply_layout(context, event):
    """Apply the layout for elements in the teaser list.

    The first one mustn't be small, all other have to be small.
    """
    # We are leaders!
    content = [content for content in context.values()
               if zeit.content.cp.interfaces.ITeaserBlock.providedBy(content)]
    if len(content) == 0:
        return
    first = content[0]
    buttons = zeit.content.cp.layout.get_layout('buttons')
    if first.layout == buttons or first.layout is None:
        first.layout = zeit.content.cp.layout.get_layout('leader')
    for elem in content[1:]:
        elem.layout = buttons


def create_xi_include(context, xpath):
    include_maker = lxml.objectify.ElementMaker(
        annotate=False,
        namespace='http://www.w3.org/2003/XInclude',
        nsmap={'xi': 'http://www.w3.org/2003/XInclude'},
    )

    # We hardcode the path here as it is not going to change any time
    # soon.
    path = context.uniqueId.replace(
        zeit.cms.interfaces.ID_NAMESPACE, '/var/cms/')

    include = include_maker.include(
        include_maker.fallback('Ziel %s nicht erreichbar.' % context.uniqueId),
        href=path,
        parse='xml',
        xpointer='xpointer(%s)' % xpath)
    return include


@zope.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def cp_xi_include(context):
    """Reference a CP as xi:include."""
    return create_xi_include(
        context, ("/centerpage/body/cluster[@area='feature']"
                  "/region[@area='lead']/container/block[1]"))


@zope.component.adapter(zeit.cms.syndication.feed.Feed)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def feed_xi_include(context):
    """Reference a Feed as xi:include.

    Note that this adapts the Feed class instead of the IFeed interface because
    the interface does not guarantee any xml structure.

    """
    return create_xi_include(context, '/channel/container/block')
