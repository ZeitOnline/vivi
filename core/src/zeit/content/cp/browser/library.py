# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Module library and landing zones.

The module library allows users to create new blocks.

See http://cmsdev.zeit.de/node/362

"""

import zeit.edit.browser.library
import zope.component


class CPBlockFactories(zeit.edit.browser.library.BlockFactories):

    @property
    def factory_context(self):
        return zeit.content.cp.area.Area(None, None)

    @property
    def library_name(self):
        return 'cp'


class CPAreaFactories(zeit.edit.browser.library.BlockFactories):

    @property
    def factory_context(self):
        return zeit.content.cp.area.Region(None, None)

    @property
    def library_name(self):
        return 'region'

    def get_adapters(self):
        element_type = 'area'
        adapter = zope.component.getAdapter(
            self.factory_context, zeit.edit.interfaces.IElementFactory,
            name=element_type)
        return [(area_config.id, element_type, area_config.title, adapter,
                 self.library_name, {'width': area_config.width})
                for area_config in zeit.content.cp.layout.AREA_CONFIGS(
                    self.context)]
