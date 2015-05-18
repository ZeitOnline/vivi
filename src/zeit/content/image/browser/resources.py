from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.content.image', 'resources')
Resource('drag-images.js', depends=[zeit.cms.browser.resources.base])
Resource('variant.css')
Resource('variant.js', depends=[zeit.cms.browser.resources.base])
