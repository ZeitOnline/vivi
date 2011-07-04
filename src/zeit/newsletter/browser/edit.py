# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.edit.browser.landing
import zeit.edit.browser.view


class LandingZoneBase(zeit.edit.browser.landing.LandingZone):

    uniqueId = zeit.edit.browser.view.Form('uniqueId')
    block_type = 'teaser'

    def initialize_block(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        self.block.reference = content


class GroupLandingZone(LandingZoneBase):
    """Handler to drop objects to the body's landing zone."""

    order = 0


class TeaserLandingZone(LandingZoneBase):
    """Handler to drop objects after other objects."""

    order = 'after-context'


class Teaser(object):

    @property
    def metadata(self):
        return zeit.cms.content.interfaces.ICommonMetadata(
            self.context.reference, None)
