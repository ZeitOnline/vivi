# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Module library and landing zones.

The module library allows users to create new blocks.

See http://cmsdev.zeit.de/node/362

"""

import zeit.content.cp.browser.landing
import zeit.edit.browser.library
import zeit.edit.browser.view
import zope.browser.interfaces
import zope.component
import zope.i18n




class ClusterBlockFactories(zeit.edit.browser.library.BlockFactories):
    # In the mosaic itself there are no blocks possible, so we have to look
    # into a teaserbar.

    @property
    def factory_context(self):
        if not self.context:
            return None
        key = self.context.keys()[0]
        return self.context[key]


class CPBlockFactories(zeit.edit.browser.library.BlockFactories):

    def get_adapters(self):
        adapters = []
        for name in ('informatives', 'teaser-mosaic'):
            region = self.context[name]
            view = zope.component.getMultiAdapter(
                (region, self.request), name=self.__name__)
            adapters.extend(view.get_adapters())
        return adapters



class BlockLandingZone(zeit.content.cp.browser.landing.LandingZone):

    block_type = zeit.edit.browser.view.Form('block_type')
    order = 'after-context'


class RegionLandingZone(zeit.content.cp.browser.landing.LandingZone):

    block_type = zeit.edit.browser.view.Form('block_type')
    order = 0
