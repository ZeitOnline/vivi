from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.wochenmarkt', 'resources')
Resource('recipe.js', depends=[zeit.cms.browser.resources.base])
