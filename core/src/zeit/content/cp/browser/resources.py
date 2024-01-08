import os.path

import fanstatic.core

from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources
import zeit.edit.browser.resources


lib = Library('zeit.content.cp', 'resources')
Resource('editor.css')

Resource(
    'editor.js',
    depends=[
        zeit.cms.browser.resources.base,
        zeit.edit.browser.resources.context_js,
        zeit.edit.browser.resources.edit_js,
        zeit.edit.browser.resources.sortable_js,
        editor_css,  # noqa
    ],
)

Resource(
    'library.js',
    depends=[
        zeit.cms.browser.resources.base,
        zeit.edit.browser.resources.library_js,
        zeit.edit.browser.resources.drop_js,
        editor_js,  # noqa
        editor_css,  # noqa
    ],
)

Resource(
    'teaser.js',
    depends=[
        zeit.cms.browser.resources.base,
        zeit.cms.browser.resources.dnd_js,
        zeit.edit.browser.resources.context_js,
        zeit.edit.browser.resources.edit_js,
        zeit.edit.browser.resources.drop_js,
        zeit.edit.browser.resources.json_js,
        editor_js,  # noqa
        editor_css,  # noqa
    ],
)


Resource(
    'area.js',
    depends=[
        zeit.cms.browser.resources.base,
    ],
)


class RawCSS:
    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/css')
        res = zeit.connector.interfaces.IResource(self.context)
        with res.data as f:
            return f.read().decode('utf-8')


class RemoteURLResource(fanstatic.core.Renderable, fanstatic.core.Dependable):
    dependency_nr = 0
    bottom = False
    dont_bundle = True

    def __init__(self, library, url):
        self.library = library
        self.url = url
        # Conform to fanstatic.core.Resource API
        self.resources = {self}
        self.order, self.renderer = fanstatic.core.inclusion_renderers['.css']
        self.relpath = os.path.basename(url)

    def render(self, library_url):
        return self.renderer(self.url + '/@@raw.css')

    def compile(self):
        pass

    def need(self, slots=None):
        needed = fanstatic.core.get_needed()
        needed.need(self, slots)
