from zeit.cms.browser.resources import Resource, Library
import fanstatic.core
import os.path
import zeit.cms.browser.resources
import zeit.edit.browser.resources


lib = Library('zeit.content.cp', 'resources')
Resource('editor.css')

Resource('editor.js', depends=[
    zeit.cms.browser.resources.base,
    zeit.edit.browser.resources.context_js,
    zeit.edit.browser.resources.edit_js,
    zeit.edit.browser.resources.sortable_js,
    editor_css,
])

Resource('library.js', depends=[
    zeit.cms.browser.resources.base,
    zeit.edit.browser.resources.library_js,
    zeit.edit.browser.resources.drop_js,
    editor_js,
    editor_css,
])

Resource('teaser.js', depends=[
    zeit.cms.browser.resources.base,
    zeit.cms.browser.resources.dnd_js,
    zeit.edit.browser.resources.context_js,
    zeit.edit.browser.resources.edit_js,
    zeit.edit.browser.resources.sortable_js,
    zeit.edit.browser.resources.drop_js,
    zeit.edit.browser.resources.json_js,
    zeit.edit.browser.resources.lightbox_js,
    editor_js,
    editor_css,
])


Resource('area.js', depends=[
    zeit.cms.browser.resources.base,
])


class RawCSS(object):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/css')
        return self.context.data


class RemoteURLResource(fanstatic.core.Renderable, fanstatic.core.Dependable):

    dependency_nr = 0
    bottom = False
    dont_bundle = True

    def __init__(self, library, url):
        self.library = library
        self.url = url
        # Conform to fanstatic.core.Resource API
        self.resources = set([self])
        self.order, self.renderer = fanstatic.core.inclusion_renderers['.css']
        self.relpath = os.path.basename(url)

    def render(self, library_url):
        return self.renderer(self.url + '/@@raw.css')

    def compile(self):
        pass

    def need(self, slots=None):
        needed = fanstatic.core.get_needed()
        needed.need(self, slots)
