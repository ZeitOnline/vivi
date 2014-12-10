# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Module library and landing zones.

The module library allows users to create new blocks.

See http://cmsdev.zeit.de/node/362

"""

import zeit.edit.browser.library
import zope.component


class CPBlockFactories(zeit.edit.browser.library.BlockFactories):

    def get_adapters(self):
        area = zeit.content.cp.area.Area(None, None)
        library_name = 'cp'
        adapters = zope.component.getAdapters(
            (area,), zeit.edit.interfaces.IElementFactory)
        return [(name, adapter, library_name) for (name, adapter) in adapters
                if adapter.title]
