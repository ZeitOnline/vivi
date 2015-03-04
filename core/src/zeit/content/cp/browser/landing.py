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


class CreateNestedAreaMixin(object):

    @property
    def create_nested_area(self):
        raise NotImplementedError("Implemented by subclass.")

    def update(self):
        super(CreateNestedAreaMixin, self).update()
        if self.create_nested_area:
            self.signal('after-reload', 'added', self.region.__name__)

    def update_order(self):
        if not self.create_nested_area:
            super(CreateNestedAreaMixin, self).update_order()
            return

        keys = list(self.container)
        keys.remove(self.region.__name__)
        keys = self.add_block_in_order(keys, self.region.__name__)
        self.container.updateOrder(keys)

    @property
    def region(self):
        if not self.create_nested_area:
            raise ValueError(
                "Should only be called when creating a nested area.")

        if not hasattr(self, '_region'):
            self._region = self.context.create_item('region')
        return self._region


class BodyLandingZone(
        CreateNestedAreaMixin,
        zeit.edit.browser.landing.LandingZone):
    """LandingZone to create a Region when the link 'Add region' is clicked.

    Can also create a region with an area inside, when an area is dropped onto
    this LandingZone.

    """

    block_type = zeit.edit.browser.view.Form('block_type')

    @property
    def create_nested_area(self):
        return self.block_type == 'area'

    @property
    def block_factory(self):
        if not self.create_nested_area:
            return super(BodyLandingZone, self).block_factory

        return zope.component.getAdapter(
            self.region, zeit.edit.interfaces.IElementFactory,
            name=self.block_type)


class BodyLandingZoneMove(
        CreateNestedAreaMixin,
        zeit.edit.browser.landing.LandingZoneMove):
    """LandingZone to sort Regions inside body.

    It is also possible to move an area onto the body to create a new region
    with the area inside.

    """

    @property
    def create_nested_area(self):
        return zeit.content.cp.interfaces.IArea.providedBy(self.block)

    def reload(self, container):
        """Skip reload of container the area came from, since we reload body.
        """
        if self.create_nested_area and container == self.old_container:
            return
        super(BodyLandingZoneMove, self).reload(container)

    def move_block(self):
        self.block = self.find_topmost_container(
            self.context).get_recursive(self.block_id)
        self.old_container = self.block.__parent__
        del self.old_container[self.block.__name__]

        if self.create_nested_area:
            self.region.add(self.block)
        else:
            self.context.add(self.block)


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
