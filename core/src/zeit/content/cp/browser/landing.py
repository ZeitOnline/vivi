# coding: utf8
"""Landing zone views.

For TeaserBlockLandingZone see: http://cmsdev.zeit.de/content/aufmacher-fläche-einen-block-anlegen-durch-ziehen-eines-content-objekts # noqa

"""

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.related.interfaces
import zeit.edit.browser.landing
import zeit.edit.browser.view
import zeit.edit.interfaces
import zope.component


class BodyLandingZone(zeit.edit.browser.landing.LandingZone):
    """LandingZone to create a Region when the link 'Add region' is clicked.

    Can also create a region with an area inside, when an area is dropped onto
    this LandingZone.

    """

    block_type = zeit.edit.browser.view.Form('block_type')

    def update(self):
        super(BodyLandingZone, self).update()
        if self.create_nested_area:
            self.signal('after-reload', 'added', self.region.__name__)

    @property
    def block_factory(self):
        if not self.create_nested_area:
            return super(BodyLandingZone, self).block_factory

        return zope.component.getAdapter(
            self.region, zeit.edit.interfaces.IElementFactory,
            name=self.block_type)

    def update_order(self):
        if not self.create_nested_area:
            super(BodyLandingZone, self).update_order()
            return

        keys = list(self.container)
        keys.remove(self.region.__name__)
        keys = self.add_block_in_order(keys, self.region.__name__)
        self.container.updateOrder(keys)

    @property
    def create_nested_area(self):
        return self.block_type == 'area'

    @property
    def region(self):
        if not self.create_nested_area:
            raise ValueError(
                "Should only be called when creating a nested area.")

        if not hasattr(self, '_region'):
            self._region = self.context.create_item('region')
        return self._region


class TeaserBlockLandingZone(zeit.edit.browser.landing.LandingZone):

    block_type = 'teaser'
    uniqueId = zeit.edit.browser.view.Form('uniqueId')
    relateds = zeit.edit.browser.view.Form(
        'relateds', json=True, default=False)

    def initialize_block(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId, None)
        if content is None:
            raise ValueError(
                _('The object "${name}" does not exist.', mapping=dict(
                    name=self.uniqueId)))
        self.block.insert(0, content)
        if self.relateds:
            related = zeit.cms.related.interfaces.IRelatedContent(
                content, None)
            if related is not None:
                for i, related in enumerate(related.related):
                    self.block.insert(i + 1, related)
