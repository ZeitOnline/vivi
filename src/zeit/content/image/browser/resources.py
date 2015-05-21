from js.backbone import backbone
from zeit.cms.browser.resources import Resource, Library
import fanstatic
import zeit.cms.browser.resources


lib = Library('zeit.content.image', 'resources')
Resource('drag-images.js', depends=[zeit.cms.browser.resources.base])
Resource('variant.css')
Resource('variant.js', depends=[
    variant_css, zeit.cms.browser.resources.base, backbone])

test_lib = fanstatic.Library('zeit.content.image.test', 'tests')
test_variant_js = fanstatic.Resource(
    test_lib, 'test_variant.js', depends=[variant_js])
