import collections
import fanstatic
import json
import os.path
import zeit.cms.browser.view
import zeit.edit.browser.landing
import zope.component
import zope.i18n


class BlockFactories(zeit.cms.browser.view.JSON):

    # XXX The block images should probably move to zeit.edit, or we should set
    # up separate BlockFactories registrations for cp, article, and newsletter
    # with their respective resource_library.
    resource_library = 'zeit.content.cp'
    template = 'block_factories.jsont'

    def json(self):
        return {'factories': self.list_block_types()}

    def list_block_types(self):
        types = collections.OrderedDict()
        for item in self.get_adapters():
            if item['name'] not in types:
                image = 'module-%s.png' % item['name']
                if not self.resource_exists(image):
                    image = 'module-default-image.png'
                image = self.resource_url(image)
                types[item['name']] = {
                    'css': ['module', 'represents-content-object'],
                    'image': image,
                    'title': zope.i18n.translate(
                        item['title'], context=self.request),
                    'type': item['type'],
                    'params': json.dumps(item['params']),
                }
            types[item['name']]['css'].append(item['library_name'] + '-module')
        for type_ in types.values():
            type_['css'] = ' '.join(type_['css'])
        return self.sort_block_types(list(types.values()))

    def sort_block_types(self, items):
        return sorted(items, key=lambda r: r['title'])

    def get_adapters(self):
        context = self.factory_context
        if context is None:
            return []
        adapters = zope.component.getAdapters(
            (context,), zeit.edit.interfaces.IElementFactory)
        return [{
            'name': name,
            'type': name,
            'title': adapter.title,
            'library_name': self.library_name,
            'params': {}
        } for (name, adapter) in adapters if adapter.title]

    @property
    def factory_context(self):
        return self.context

    @property
    def library_name(self):
        return self.context.__name__

    def resource_exists(self, filename):
        library = fanstatic.get_library_registry()[self.resource_library]
        return os.path.exists(os.path.join(library.path, filename))


class BlockLandingZone(zeit.edit.browser.landing.LandingZone):

    block_type = zeit.edit.browser.view.Form('block_type')
    order = 'after-context'


class AreaLandingZone(zeit.edit.browser.landing.LandingZone):

    block_type = zeit.edit.browser.view.Form('block_type')
    order = 0
