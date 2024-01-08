from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.cmp', 'resources')
Resource('cmp.js', depends=[zeit.cms.browser.resources.base])
