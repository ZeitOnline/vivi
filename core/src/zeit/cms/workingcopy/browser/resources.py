from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.cms.workingcopy', 'resources')
Resource('workingcopy.js', depends=[zeit.cms.browser.resources.base])
