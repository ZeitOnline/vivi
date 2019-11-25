from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.content.volume', 'resources')
Resource('volume-covers.js', depends=[zeit.cms.browser.resources.base])
Resource('filteringcontenttable.js', depends=[zeit.cms.browser.resources.base])