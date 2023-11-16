from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.cmp', 'resources')
Resource('cmp.js', depends=[zeit.cms.browser.resources.base])
