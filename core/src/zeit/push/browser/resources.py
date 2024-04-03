from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.push', 'resources')
Resource('push.css')
Resource('mobile.js', depends=[zeit.cms.browser.resources.base])
