from zeit.cms.testing import copy_inherited_functions
import zeit.cms.content.tests.test_contentsource
import zeit.cms.testing
import zeit.content.gallery.interfaces
import zeit.content.gallery.testing


class TestGallerySource(
    zeit.cms.content.tests.test_contentsource.ContentSourceBase,
    zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.gallery.testing.ZCML_LAYER

    source = zeit.content.gallery.interfaces.gallerySource
    expected_types = ['gallery']

    copy_inherited_functions(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase,
        locals())
