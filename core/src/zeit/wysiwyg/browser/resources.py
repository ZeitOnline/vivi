from fanstatic import Library, Resource
from gocept.fckeditor.resources import fckeditor

import zeit.cms.browser.resources


lib = Library('zeit.wysiwyg', 'resources')
common_css = Resource(lib, 'common.css')
wysiwyg = Resource(
    lib, 'common.js', depends=[zeit.cms.browser.resources.base, fckeditor, common_css]
)
