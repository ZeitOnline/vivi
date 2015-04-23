# coding: utf8
"""Landing zone views.

For TeaserBlockLandingZone see: http://cmsdev.zeit.de/content/aufmacher-fläche-einen-block-anlegen-durch-ziehen-eines-content-objekts # noqa

"""

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.related.interfaces
import zeit.content.cp.interfaces
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

    def reload(self, container):
        """Skip reload of the created region, since it is not present yet.

        The reload is triggered since nesting the area inside region creates a
        IContainerModifiedEvent, which trigger_reload subscribes to.

        """
        if zeit.content.cp.interfaces.IRegion.providedBy(container):
            return
        super(CreateNestedAreaMixin, self).reload(container)

    @property
    def region(self):
        if not self.create_nested_area:
            raise ValueError(
                "Should only be called when creating a nested area.")

        if not hasattr(self, '_region'):
            # create region at position given by arguments
            position = self.get_position_from_order(self.container.keys())
            self._region = self.context.create_item('region', position)
        return self._region


class BodyLandingZoneRegion(zeit.edit.browser.landing.LandingZone):
    """LandingZone to create a Region (potentially with areas inside it).

    """

    block_type = zeit.edit.browser.view.Form('block_type')

    def update(self):
        self.areas = self.block_params.pop('areas', [])
        super(BodyLandingZoneRegion, self).update()

    def initialize_block(self):
        super(BodyLandingZoneRegion, self).initialize_block()
        for config in self.areas:
            area = self.block.create_item('area')
            area.width = config['width']


class BodyLandingZoneArea(
        CreateNestedAreaMixin,
        zeit.edit.browser.landing.LandingZone):
    """LandingZone that creates a Region when an Area is dropped.

    """

    block_type = zeit.edit.browser.view.Form('block_type')

    @property
    def create_nested_area(self):
        return self.block_type == 'area'

    @property
    def block_factory(self):
        """Overwrite to use self.region instead of self.container as parent."""
        if not self.create_nested_area:
            return super(BodyLandingZoneArea, self).block_factory

        return zope.component.getAdapter(
            self.region, zeit.edit.interfaces.IElementFactory,
            name=self.block_type)

    def create_block(self):
        """Overwrite to ignore positional arguments.

        The position is only relevant to child of Body, i.e. regions. This
        logic is handled in the region property. The area is always the only
        item in region, since the region was just created. Thus any positional
        arguments are irrelevant.

        """
        if not self.create_nested_area:
            super(BodyLandingZoneArea, self).create_block()
            return
        self.block = self.block_factory()


class BodyLandingZoneMove(
        CreateNestedAreaMixin,
        zeit.edit.browser.landing.LandingZoneMove):
    """LandingZone to sort Regions inside body.

    It is also possible to move an area onto the body to create a new region
    with the area inside.

    """

    @property
    def create_nested_area(self):
        return (hasattr(self, 'block')
                and zeit.content.cp.interfaces.IArea.providedBy(self.block))

    def move_block(self):
        """Overwrite to move area into the newly created region.

        Normally the move event would try to insert the area into body, which
        obviously doesn't work. (The hierarchy is Body > Region > Area).

        """
        # setup self.block before calling self.create_nested_area
        self.block = self.find_topmost_container(
            self.context).get_recursive(self.block_id)
        self.old_container = self.block.__parent__

        if not self.create_nested_area:
            super(BodyLandingZoneMove, self).move_block()
            return

        del self.old_container[self.block.__name__]
        self.region.add(self.block)


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
