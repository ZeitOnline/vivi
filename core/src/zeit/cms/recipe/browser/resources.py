from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.cms.recipe', 'resources')
Resource('recipe.js', depends=[zeit.cms.browser.resources.base])
