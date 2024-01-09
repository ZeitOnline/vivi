from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.cms.tagging', 'resources')
Resource('tag.js', depends=[zeit.cms.browser.resources.base])
