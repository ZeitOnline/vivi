# coding: utf8
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Landing zone views.

See: http://cmsdev.zeit.de/content/aufmacher-fläche-einen-block-anlegen-durch-ziehen-eines-content-objekts

"""

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.related.interfaces
import zeit.edit.browser.view
import zeit.edit.browser.landing


class TeaserBlockLandingZone(zeit.edit.browser.landing.LandingZone):

    block_type = 'teaser'
    uniqueId = zeit.edit.browser.view.Form('uniqueId')
    relateds = zeit.edit.browser.view.Form(
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
