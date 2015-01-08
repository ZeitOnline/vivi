from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.cms.sitecontrol', 'resources')
Resource('sidebar.js', depends=[zeit.cms.browser.resources.base])
