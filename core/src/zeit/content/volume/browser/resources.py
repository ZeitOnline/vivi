from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources

lib = Library('zeit.content.volume', 'resources')
Resource('toclisting.css', depends=[zeit.cms.browser.resources.base])
Resource('volume-covers.js', depends=[zeit.cms.browser.resources.base])
Resource('filtertoclisting.js', depends=[zeit.cms.browser.resources.base])