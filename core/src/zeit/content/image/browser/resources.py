from js.backbone import backbone
from js.cropper import cropper
from js.handlebars import handlebars
from zeit.cms.browser.resources import Resource, Library
import fanstatic
import zeit.cms.browser.resources


lib = Library('zeit.content.image', 'resources')
Resource('drag-images.js', depends=[zeit.cms.browser.resources.base])
Resource('imagegroup.css')
Resource('variant.css')
Resource('variant.js', depends=[
    variant_css, zeit.cms.browser.resources.base,
    backbone, cropper, handlebars])

Resource('form.js', depends=[zeit.cms.browser.resources.base])
Resource('mdb.js', depends=[zeit.cms.browser.resources.base])

test_lib = fanstatic.Library('zeit.content.image.test', 'tests')
test_variant_js = fanstatic.Resource(
    test_lib, 'test_variant.js', depends=[variant_js])
