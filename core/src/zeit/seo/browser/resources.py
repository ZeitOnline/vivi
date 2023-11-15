from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.seo', 'resources')
Resource(
    'counter.js', depends=[zeit.cms.browser.resources.base, zeit.cms.browser.resources.counter_js]
)
