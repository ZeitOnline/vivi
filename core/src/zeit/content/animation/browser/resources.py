# ruff: noqa: F821
from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.content.animation', 'resources')
Resource('form.js', depends=[zeit.cms.browser.resources.base])
