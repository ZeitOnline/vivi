from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.cms.clipboard', 'resources')
Resource(
    'clipboard.js', depends=[zeit.cms.browser.resources.base, zeit.cms.browser.resources.dnd_js]
)
