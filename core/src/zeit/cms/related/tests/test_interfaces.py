from zeit.cms.content.contentsource import cmsContentSource
from zeit.cms.related.interfaces import relatableContentSource
import zeit.cms.config
import zeit.cms.content.contentsource
import zeit.cms.testing


class Source(zeit.cms.testing.ZeitCmsTestCase):
    def test_asterisk_means_return_all_content_types(self):
        self.assertEqual(
            cmsContentSource.get_check_interfaces(), relatableContentSource.get_check_interfaces()
        )

    def test_valid_interfaces_are_returned_in_order(self):
        zeit.cms.config.set(
            'zeit.cms',
            'relatable-content-types',
            'zeit.cms.repository.interfaces.IFolder '
            'zeit.cms.testcontenttype.interfaces.IExampleContentType',
        )
        self.assertEqual(
            [
                zeit.cms.repository.interfaces.IFolder,
                zeit.cms.testcontenttype.interfaces.IExampleContentType,
            ],
            relatableContentSource.get_check_interfaces(),
        )

    def test_invalid_interface_raises_typeerror(self):
        zeit.cms.config.set(
            'zeit.cms',
            'relatable-content-types',
            'zeit.cms.repository.interfaces.IFolder zope.interface.Interface',
        )
        with self.assertRaises(TypeError):
            relatableContentSource.get_check_interfaces()
