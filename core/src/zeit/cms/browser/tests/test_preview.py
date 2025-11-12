import zope.component

from zeit.cms.browser.interfaces import IPreviewURL
from zeit.cms.browser.preview import prefixed_url
import zeit.cms.testing


class PreviewTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_invalid_unique_ids_should_raise_valueerror(self):
        self.assertRaises(ValueError, prefixed_url, 'aprefix', 'foo')

    def test_adapting_cmscontent_should_return_preview_url(self):
        self.assertEqual(
            'http://localhost/preview-prefix/testcontent',
            zope.component.getMultiAdapter(
                (self.repository['testcontent'], 'preview'), IPreviewURL
            ),
        )
