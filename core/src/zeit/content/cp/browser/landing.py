# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Landing zone view.

See: http://cmsdev.zeit.de/content/aufmacher-fläche-einen-block-anlegen-durch-ziehen-eines-content-objekts

"""

import zeit.cms.browser.view
import zeit.cms.related.interfaces
import zope.browser.interfaces
import zope.component


class LandingZone(zeit.cms.browser.view.Base):

    def __call__(self, uniqueId):
        teaser_block = self.create_block(uniqueId)
        order = list(self.create_in)
        order.remove(teaser_block.__name__)
        order = self.get_order(order, teaser_block.__name__)
        self.create_in.updateOrder(order)
        # XXX notify event
        return self.url(teaser_block)

    def create_block(self, uniqueId):
        factory = zope.component.getAdapter(
            self.create_in, zeit.content.cp.interfaces.IBlockFactory,
            name='teaser')
        teaser_block = factory()
        content = zeit.cms.interfaces.ICMSContent(uniqueId)
        teaser_block.insert(0, content)
        related = zeit.cms.related.interfaces.IRelatedContent(content, None)
        if related is not None:
            for i, related in enumerate(related.related):
                teaser_block.insert(i+1, related)
        teaser_block.layout = self.layouts.getValue('leader')
        return teaser_block

    @property
    def layouts(self):
        return zope.component.getMultiAdapter(
            (zeit.content.cp.interfaces.ITeaserBlock['layout'].source,
             self.request),
            zope.browser.interfaces.ITerms)


class LeaderLandingZoneDrop(LandingZone):
    """Handler to drop articles on the lead landing zone."""

    def get_order(self, order, new_name):
        order.insert(0, new_name)
        return order

    @property
    def create_in(self):
        return self.context

class TeaserLandingZoneInsertAfter(LandingZone):

    def get_order(self, order, new_name):
        after = order.index(self.context.__name__)
        order.insert(after + 1, new_name)
        return order

    @property
    def create_in(self):
        return self.context.__parent__
