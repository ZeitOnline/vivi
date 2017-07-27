from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.push', 'resources')
Resource('push.css')
Resource('social.js', depends=[zeit.cms.browser.resources.base])
Resource('mobile.js', depends=[zeit.cms.browser.resources.base])
