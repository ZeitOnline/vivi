from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.cms.tagging', 'resources')
Resource('tag.js', depends=[zeit.cms.browser.resources.base])
