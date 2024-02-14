# ruff: noqa: F821
from js.backbone import backbone
from js.cropper import cropper
from js.handlebars import handlebars

from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources


lib = Library('zeit.content.image', 'resources')
Resource('drag-images.js', depends=[zeit.cms.browser.resources.base])
Resource('imagegroup.css')
Resource('variant.css')
Resource(
    'variant.js',
    depends=[
        variant_css,
        zeit.cms.browser.resources.base,
        backbone,
        cropper,
        handlebars,
    ],
)

Resource('form.js', depends=[zeit.cms.browser.resources.base])
Resource('mdb.js', depends=[zeit.cms.browser.resources.base])
