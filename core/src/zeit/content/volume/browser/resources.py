from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources

lib = Library('zeit.content.volume', 'resources')
Resource('contentlisting.css', depends=[zeit.cms.browser.resources.base])
Resource('volume-covers.js', depends=[zeit.cms.browser.resources.base])
Resource('filteringcontenttable.js', depends=[zeit.cms.browser.resources.base])