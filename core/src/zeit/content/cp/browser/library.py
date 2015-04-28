"""Module library and landing zones.

The module library allows users to create new blocks.

See http://cmsdev.zeit.de/node/362

"""

import lxml.objectify
import zeit.edit.browser.library


class CPBlockFactories(zeit.edit.browser.library.BlockFactories):

    @property
    def factory_context(self):
        xml = lxml.objectify.XML('<dummy/>')
        return zeit.content.cp.area.Area(None, xml)

    @property
    def library_name(self):
        return 'cp'


class CPAreaFactories(zeit.edit.browser.library.BlockFactories):

    @property
    def factory_context(self):
        xml = lxml.objectify.XML('<dummy/>')
        return zeit.content.cp.area.Region(None, xml)

    @property
    def library_name(self):
        return 'region'

    def get_adapters(self):
        return [{
            'name': 'area-%s' % i,
            'type': 'area',
            'title': area_config.title,
            'library_name': self.library_name,
            'params': {'kind': area_config.kind}
        } for i, area_config in enumerate(
            zeit.content.cp.layout.AREA_CONFIGS(self.context))]


class CPRegionFactories(zeit.edit.browser.library.BlockFactories):

    @property
    def factory_context(self):
        xml = lxml.objectify.XML('<dummy/>')
        return zeit.content.cp.centerpage.Body(None, xml)

    @property
    def library_name(self):
        return 'body'

    def get_adapters(self):
        return [{
            'name': 'region-%s' % i,
            'type': 'region',
            'title': region_config.title,
            'library_name': self.library_name,
            'params': {
                'kind': region_config.kind,
                'areas': region_config.areas,
            },
        } for i, region_config in enumerate(
            zeit.content.cp.layout.REGION_CONFIGS(self.context))]
