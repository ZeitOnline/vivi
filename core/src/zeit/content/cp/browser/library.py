# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Module library and landing zones.

The module library allows users to create new blocks.

See http://cmsdev.zeit.de/node/362

"""

import zeit.edit.browser.library


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
