from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.wochenmarkt', 'resources')
Resource('recipe.js', depends=[zeit.cms.browser.resources.base])
