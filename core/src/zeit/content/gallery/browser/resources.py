# ruff: noqa: F821
import fanstatic

from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.content.gallery', 'resources')
Resource('gallery.css')

Resource('details.js', depends=[zeit.cms.browser.resources.base, gallery_css])

swfupload = fanstatic.Resource(lib, 'SWFUpload/swfupload.js')
Resource(
    'upload.js',
    depends=[
        zeit.cms.browser.resources.base,
        zeit.cms.browser.resources.filename_js,
        swfupload,
        gallery_css,
    ],
)
