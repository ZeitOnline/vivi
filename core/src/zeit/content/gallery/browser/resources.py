# ruff: noqa: F821
from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.content.gallery', 'resources')
Resource('gallery.css')

Resource('details.js', depends=[zeit.cms.browser.resources.base, gallery_css])
