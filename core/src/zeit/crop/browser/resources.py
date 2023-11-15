from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.crop', 'resources')
Resource('ui4w.css')
Resource('ui4w.js', depends=[ui4w_css])  # noqa
Resource('imp.css')
Resource('imp.js', depends=[zeit.cms.browser.resources.base, ui4w_js, imp_css])  # noqa
