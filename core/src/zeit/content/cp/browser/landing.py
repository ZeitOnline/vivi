# coding: utf8
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Landing zone views.

See: http://cmsdev.zeit.de/content/aufmacher-fläche-einen-block-anlegen-durch-ziehen-eines-content-objekts

"""

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.related.interfaces
import zeit.content.cp.browser.view
import zope.browser.interfaces
import zope.component


class LandingZone(zeit.content.cp.browser.view.Action):

    def update(self):
        self.create_block()
        self.initialize_block()
        self.update_order()
        self.signal('after-reload', 'added', self.block.__name__)
        self.signal(
            None, 'reload',
            self.create_in.__name__, self.url(self.create_in, '@@contents'))

    def create_block(self):
        factory = zope.component.getAdapter(
            self.create_in, zeit.edit.interfaces.IElementFactory,
            name=self.block_type)
        self.block = factory()
        assert zeit.content.cp.centerpage.has_changed(self.context)

    def initialize_block(self):
        pass

    def update_order(self):
        order = list(self.create_in)
        order.remove(self.block.__name__)
        order = self.get_order(order, self.block.__name__)
        self.create_in.updateOrder(order)
        assert zeit.content.cp.centerpage.has_changed(self.create_in)

    @property
    def create_in(self):
        if self.order == 'after-context':
            return self.context.__parent__
        return self.context

    def get_order(self, order, new_name):
        if isinstance(self.order, int):
            order.insert(self.order, new_name)
        elif self.order == 'after-context':
            after = order.index(self.context.__name__)
            order.insert(after + 1, new_name)
        else:
            raise NotImplementedError
        return order


class TeaserBlockLandingZone(LandingZone):

    block_type = 'teaser'
    uniqueId = zeit.content.cp.browser.view.Form('uniqueId')
    relateds = zeit.content.cp.browser.view.Form(
        'relateds', json=True, default=True)

    def initialize_block(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId, None)
        if content is None:
            raise ValueError(
                _('The object "${name}" does not exist.', mapping=dict(
                    name=self.uniqueId)))
        self.block.insert(0, content)
        if self.relateds:
            related = zeit.cms.related.interfaces.IRelatedContent(content, None)
            if related is not None:
                for i, related in enumerate(related.related):
                    self.block.insert(i+1, related)


class LeaderLandingZoneDrop(TeaserBlockLandingZone):
    """Handler to drop articles on the lead landing zone."""

    order = 0


class TeaserLandingZoneInsertAfter(TeaserBlockLandingZone):

    order = 'after-context'
