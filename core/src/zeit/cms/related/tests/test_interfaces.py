from zeit.cms.content.contentsource import cmsContentSource
from zeit.cms.related.interfaces import relatableContentSource
import zeit.cms.content.contentsource
import zeit.cms.testing
import zope.app.appsetup.product


class Source(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        self.product_config = \
            zope.app.appsetup.product.getProductConfiguration('zeit.cms')

    def test_asterisk_means_return_all_content_types(self):
        self.assertEqual(
            cmsContentSource.get_check_interfaces(),
            relatableContentSource.get_check_interfaces())

    def test_valid_interfaces_are_returned_in_order(self):
        self.product_config['relatable-content-types'] = (
            'zeit.cms.repository.interfaces.IFolder '
            'zeit.cms.testcontenttype.interfaces.ITestContentType')
        self.assertEqual(
            [zeit.cms.repository.interfaces.IFolder,
             zeit.cms.testcontenttype.interfaces.ITestContentType],
            relatableContentSource.get_check_interfaces())

    def test_invalid_interface_raises_typeerror(self):
        self.product_config['relatable-content-types'] = (
            'zeit.cms.repository.interfaces.IFolder '
            'zope.interface.Interface')
        with self.assertRaises(TypeError):
            relatableContentSource.get_check_interfaces()
