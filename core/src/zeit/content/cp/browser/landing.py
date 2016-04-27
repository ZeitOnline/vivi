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


class BodyLandingZone(zeit.edit.browser.landing.LandingZone):
    """LandingZone to create a Region (potentially with areas inside it).

    """

    block_type = zeit.edit.browser.view.Form('block_type')

    def update(self):
        self.areas = self.block_params.pop('areas', [])
        super(BodyLandingZone, self).update()

    def initialize_block(self):
        super(BodyLandingZone, self).initialize_block()
        for config in self.areas:
            area = self.block.create_item('area')
            area.kind = config.pop('kind')
            for name, value in config.items():
                field = zeit.content.cp.interfaces.IArea[name].bind(area)
                # We (ab)use the DAV type conversion for a `fromUnicode` that
                # supports Sources, because the mechanics are all there already
                value = zeit.cms.content.interfaces.IDAVPropertyConverter(
                    field).fromProperty(value)
                field.set(area, value)


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
