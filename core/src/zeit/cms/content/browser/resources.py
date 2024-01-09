from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.cms.content', 'resources')
Resource('teaser.js', depends=[zeit.cms.browser.resources.base])
Resource('dropdown.js', depends=[zeit.cms.browser.resources.base])
Resource('mobile_alternative.js', depends=[zeit.cms.browser.resources.base])
