from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.workflow', 'resources')
Resource('workflow.css')
Resource('publish.js', depends=[zeit.cms.browser.resources.base])
