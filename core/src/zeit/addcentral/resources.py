from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.addcentral', 'resources')
Resource('addcentral.css', depends=[zeit.cms.browser.resources.base])

# XXX zeit.addcentral needs zeit.content.browser.resources.dropdown_js,
# should we declare that somehow or simply trust the fact that all JS
# will be available everywhere?
