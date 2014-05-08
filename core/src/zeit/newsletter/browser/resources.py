from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources
import zeit.edit.browser.resources


lib = Library('zeit.newsletter', 'resources')
Resource('editor.js', depends=[
    zeit.cms.browser.resources.base,
    zeit.edit.browser.resources.context_js,
    zeit.edit.browser.resources.edit_js,
    zeit.edit.browser.resources.sortable_js,
    zeit.edit.browser.resources.json_js,
])
Resource('editor.css')
