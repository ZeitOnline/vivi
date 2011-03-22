# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Module library and landing zones.

The module library allows users to create new blocks.

See http://cmsdev.zeit.de/node/362

"""

import zeit.cms.browser.view
import zeit.content.cp.browser.landing
import zope.browser.interfaces
import zope.component
import zope.i18n


class BlockFactories(zeit.cms.browser.view.JSON):

    resource_library = 'zeit.content.cp'
    template = 'block_factories.jsont'

    def json(self):
        return dict(factories=self.list_block_types())

    def list_block_types(self):
        types = {}
        for name, adapter, library_name in self.get_adapters():
            if name not in types:
                image = self.resources.get('module-%s.png' % name, None)
                if image is None:
                    image = self.resources['module-default-image.png']
                image = image()
                types[name] = dict(
                    css=['module'],
                    image=image,
                    title=zope.i18n.translate(adapter.title,
                                              context=self.request),
                    type=name,
                )
            types[name]['css'].append(library_name + '-module')
        for type_ in types.values():
            type_['css'] = ' '.join(type_['css'])
        return sorted(types.values(), key=lambda r: r['title'])

    def get_adapters(self):
        context = self.factory_context
        if context is None:
            return []
        library_name = self.context.__name__
        adapters = zope.component.getAdapters(
            (context,), zeit.content.cp.interfaces.IElementFactory)
        return [(name, adapter, library_name) for (name, adapter) in adapters
                if adapter.title]

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


class CPBlockFactories(BlockFactories):

    def get_adapters(self):
        adapters = []
        for name in ('lead', 'informatives', 'teaser-mosaic'):
            region = self.context[name]
            view = zope.component.getMultiAdapter(
                (region, self.request), name=self.__name__)
            adapters.extend(view.get_adapters())
        return adapters



class BlockLandingZone(zeit.content.cp.browser.landing.LandingZone):

    block_type = zeit.content.cp.browser.view.Form('block_type')
    order = 'after-context'


class RegionLandingZone(zeit.content.cp.browser.landing.LandingZone):

    block_type = zeit.content.cp.browser.view.Form('block_type')
    order = 0
