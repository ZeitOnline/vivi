# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import lxml.objectify
import rwproperty
import zeit.cms.content.property
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
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
            return [zeit.cms.interfaces.ICMSContent(id) for id in self.keys()]
        else:
            return super(TeaserBlock, self).iterentries()

    def keys(self):
        if self.autopilot:
            return zeit.content.cp.interfaces.ILeadTeasers(self.referenced_cp)
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
        if not autopilot:
            self._autopilot = autopilot
            try:
                include = self.xml[
                    '{http://www.w3.org/2003/XInclude}include']
            except AttributeError:
                pass
            else:
                self.xml.remove(include)

            if self.referenced_cp:
                repository = zope.component.getUtility(
                    zeit.cms.repository.interfaces.IRepository)
                for position, id in enumerate(
                    zeit.content.cp.interfaces.ILeadTeasers(
                        self.referenced_cp)):
                    self.insert(position, repository.getContent(id))
        else:
            self.clear()
            include_maker = lxml.objectify.ElementMaker(
                annotate=False,
                namespace='http://www.w3.org/2003/XInclude',
                nsmap={'xi': 'http://www.w3.org/2003/XInclude'},
            )

            # We hardcode the path here as it is not going to change any time
            # soon.
            path = self.referenced_cp.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE, '/var/cms/')

            # NOTE: The xpointer will change when a channel is included.
            self.xml.append(include_maker.include(
                include_maker.fallback('Channel nicht erreichbar.'),
                href=path,
                parse='xml',
                xpointer=("xpointer(/centerpage/body/cluster[@area='feature']"
                          "/region[@area='lead']/container/block[1]"),
            ))
            self._autopilot = autopilot

    def clear(self):
        if not self.autopilot:
            for entry in self:
                self.remove(entry)

    @rwproperty.getproperty
    def layout(self):
        for layout in zeit.content.cp.interfaces.ITeaserBlock['layout'].source(self):
            if layout.id == self.xml.get('module'):
                return layout
        return zeit.content.cp.interfaces.IReadTeaserBlock['layout'].missing_value

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


@zope.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@zope.interface.implementer(zeit.content.cp.interfaces.ILeadTeasers)
def lead_teasers_for_centerpage(cp):
    result = []
    for block in cp['lead'].values():
        if zeit.content.cp.interfaces.ITeaserBlock.providedBy(block):
            try:
                result.append(iter(block).next().uniqueId)
            except StopIteration:
                pass
    return result


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

