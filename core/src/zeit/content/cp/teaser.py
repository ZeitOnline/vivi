# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import lxml.etree
import lxml.objectify
import zeit.cms.content.property
import zeit.cms.repository.interfaces
import zeit.cms.syndication.feed
import zeit.cms.syndication.interfaces
import zeit.content.cp.block
import zeit.content.cp.interfaces
import zope.component
import zope.container.interfaces
import zope.interface


# TeaserList reuses Feed for its "list of ICMSContent" behaviour
class TeaserList(zeit.content.cp.block.Block,
                 zeit.cms.syndication.feed.Feed):

    zope.interface.implementsOnly(
        zeit.content.cp.interfaces.ITeaserList,
        zeit.cms.syndication.interfaces.IFeed,
        zope.container.interfaces.IContained)

    # XXX XSLT must drop these
    _autopilot = zeit.cms.content.property.ObjectPathProperty('.autopilot')
    referenced_cp = zeit.cms.content.property.SingleResource('.referenced_cp')

    # overriden so that super.insert() and updateOrder() work
    @property
    def entries(self):
        return self.xml

    def iterentries(self):
        if self.autopilot:
            return iter(
                zeit.content.cp.interfaces.ILeadTeasers(self.referenced_cp))
        else:
            return super(TeaserList, self).iterentries()

    def keys(self):
        if self.autopilot:
            return zeit.content.cp.interfaces.ILeadTeasers(self.referenced_cp)
        else:
            return super(TeaserList, self).keys()

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
            return getattr(super(TeaserList, self), method)(*args, **kw)

    def _get_autopilot(self):
        return self._autopilot

    def _set_autopilot(self, autopilot):
        if autopilot == self._autopilot:
            return

        # we need to manipulate self.entries, which is only allowed while not on
        # autopilot. Thus we switch the autopilot mode at different times.
        if not autopilot:
            self._autopilot = autopilot
            if hasattr(self.xml, 'xi_include'):
                self.xml.remove(self.xml.xi_include)

            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            for position, id in enumerate(
                zeit.content.cp.interfaces.ILeadTeasers(self.referenced_cp)):
                self.insert(position, repository.getContent(id))
        else:
            self.clear()
            # XXX what is the actual syntax for xi:include needed here?
            self.xml.append(lxml.objectify.E.xi_include(
                href=self.referenced_cp.uniqueId))
            self._autopilot = autopilot

    autopilot = property(_get_autopilot, _set_autopilot)

    def clear(self):
        if not self.autopilot:
            for entry in self:
                self.remove(entry)


TeaserListFactory = zeit.content.cp.block.blockFactoryFactory(
    zeit.content.cp.interfaces.IRegion,
    TeaserList, 'teaser', _('List of teasers'))


@zope.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@zope.interface.implementer(zeit.content.cp.interfaces.ILeadTeasers)
def lead_teasers_for_centerpage(cp):
    result = []
    for block in cp['lead'].values():
        if zeit.content.cp.interfaces.ITeaserList.providedBy(block):
            try:
                result.append(iter(block).next().uniqueId)
            except StopIteration:
                pass
    return result
