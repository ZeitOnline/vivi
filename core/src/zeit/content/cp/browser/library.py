"""Module library and landing zones.

The module library allows users to create new blocks.

See http://cmsdev.zeit.de/node/362

"""

import zeit.edit.browser.library


class CPBlockFactories(zeit.edit.browser.library.BlockFactories):
    @property
    def library_name(self):
        return 'cp'

    def get_adapters(self):
        return [
            {
                'name': module.id,
                'type': module.id,
                'title': module.title,
                'library_name': self.library_name,
                'params': {},
            }
            for i, module in enumerate(zeit.content.cp.layout.MODULE_CONFIGS(self.context))
        ]

    def sort_block_types(self, items):
        # Use order defined by the source.
        return items


class CPAreaFactories(zeit.edit.browser.library.BlockFactories):
    @property
    def library_name(self):
        return 'region'

    def get_adapters(self):
        return [
            {
                'name': 'area-%s' % i,
                'type': 'area',
                'title': area_config.title,
                'library_name': self.library_name,
                'params': {'kind': area_config.kind},
            }
            for i, area_config in enumerate(zeit.content.cp.layout.AREA_CONFIGS(self.context))
        ]

    def sort_block_types(self, items):
        # Use order defined by the source.
        return items


class CPRegionFactories(zeit.edit.browser.library.BlockFactories):
    @property
    def library_name(self):
        return 'body'

    def get_adapters(self):
        return [
            {
                'name': 'region-%s' % i,
                'type': 'region',
                'title': region_config.title,
                'library_name': self.library_name,
                'params': {
                    'kind': region_config.kind,
                    'kind_title': region_config.title,
                    'areas': region_config.areas,
                },
            }
            for i, region_config in enumerate(zeit.content.cp.layout.REGION_CONFIGS(self.context))
        ]

    def sort_block_types(self, items):
        # Use order defined by the source.
        return items
