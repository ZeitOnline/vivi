# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Module library.

The module library allows users to create new blocks.

See http://cmsdev.zeit.de/node/362

"""

import zeit.cms.browser.view
import zope.component


class BlockFactories(zeit.cms.browser.view.JSON):

    resource_library = 'zeit.content.cp'
    template = 'block_factories.jsont'

    def json(self):
        return dict(factories=self.list_block_types())

    def list_block_types(self):
        context = self.factory_context
        if context is None:
            return []
        result = []
        for name, adapter in zope.component.getAdapters(
            (context,),
            zeit.content.cp.interfaces.IBlockFactory):
            if adapter.title is None:
                continue
            result.append(dict(
                type=name,
                title=adapter.title))
        return result

    @property
    def factory_context(self):
        return self.context


class ClusterBlockFactories(BlockFactories):
    # In the mosaic itself there are no blocks possible, so we have to look
    # into a teaserbar.

    @property
    def factory_context(self):
        if not self.context:
            return None
        key = self.context.keys()[0]
        return self.context[key]
