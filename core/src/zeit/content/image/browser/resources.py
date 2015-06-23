from js.backbone import backbone
from zeit.cms.browser.resources import Resource, Library
import fanstatic
import zeit.cms.browser.resources


lib = Library('zeit.content.image', 'resources')
Resource('drag-images.js', depends=[zeit.cms.browser.resources.base])
Resource('cropper.js')
Resource('cropper.css')
Resource('variant.css', depends=[cropper_css])
Resource('variant.js', depends=[
    cropper_js, variant_css, zeit.cms.browser.resources.base, backbone])

test_lib = fanstatic.Library('zeit.content.image.test', 'tests')
test_variant_js = fanstatic.Resource(
    test_lib, 'test_variant.js', depends=[variant_js])
