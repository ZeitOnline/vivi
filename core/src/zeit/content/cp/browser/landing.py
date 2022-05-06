# coding: utf8
"""Landing zone views.

For TeaserBlockLandingZone see: http://cmsdev.zeit.de/content/aufmacher-fläche-einen-block-anlegen-durch-ziehen-eines-content-objekts # noqa

"""

from zeit.cms.i18n import MessageFactory as _
from zeit.content.gallery.interfaces import IGallery
import zeit.connector.resource
import zeit.content.cp.interfaces
import zeit.edit.browser.landing
import zeit.edit.browser.view
import zope.component


class BodyLandingZone(zeit.edit.browser.landing.LandingZone):
    """LandingZone to create a Region (potentially with areas inside it).

    """

    block_type = zeit.edit.browser.view.Form('block_type')
    DUMMY_PROPS = zeit.connector.resource.WebDAVProperties()

    def update(self):
        self.areas = self.block_params.pop('areas', [])
        super().update()

    def initialize_block(self):
        super().initialize_block()
        for config in self.areas:
            area = self.block.create_item('area')
            area.kind = config.pop('kind')
            for name, value in config.items():
                field = zeit.content.cp.interfaces.IArea[name].bind(area)
                # We (ab)use the DAV type conversion for a `fromUnicode` that
                # supports Sources, because the mechanics are all there already
                converter = zope.component.getMultiAdapter(
                    (field, self.DUMMY_PROPS),
                    zeit.cms.content.interfaces.IDAVPropertyConverter)
                value = converter.fromProperty(value)
                field.set(area, value)


class ContentLandingZone(zeit.edit.browser.landing.LandingZone):

    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def create_block(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId, None)
        if content is None:
            raise ValueError(
                _('The object "${name}" does not exist.', mapping=dict(
                    name=self.uniqueId)))
        # XXX Gnarly edge case. The JS-based drag/drop handlers can only
        # differentiate by content-type, and don't have more details.
        if IGallery.providedBy(content) and content.type == 'inline':
            raise ValueError(
                _('Gallery "${name}" with type inline is not allowed here.',
                  mapping=dict(name=self.uniqueId)))
        position = self.get_position_from_order(self.container.keys())
        self.block = zope.component.getMultiAdapter(
            (self.container, content, position),
            zeit.edit.interfaces.IElement)
