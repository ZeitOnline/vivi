# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import fanstatic
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
        return dict(factories=self.list_block_types())

    def list_block_types(self):
        types = {}
        for name, adapter, library_name in self.get_adapters():
            if name not in types:
                image = 'module-%s.png' % name
                if not self.resource_exists(image):
                    image = 'module-default-image.png'
                image = self.resource_url(image)
                types[name] = dict(
                    css=['module', 'represents-content-object'],
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
            (context,), zeit.edit.interfaces.IElementFactory)
        return [(name, adapter, library_name) for (name, adapter) in adapters
                if adapter.title]

    @property
    def factory_context(self):
        return self.context

    def resource_exists(self, filename):
        library = fanstatic.get_library_registry()[self.resource_library]
        return os.path.exists(os.path.join(library.path, filename))


class BlockLandingZone(zeit.edit.browser.landing.LandingZone):

    block_type = zeit.edit.browser.view.Form('block_type')
    order = 'after-context'


class AreaLandingZone(zeit.edit.browser.landing.LandingZone):

    block_type = zeit.edit.browser.view.Form('block_type')
    order = 0
