from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.browser.interfaces
import zeit.cms.testing
import zeit.magazin.interfaces
import zeit.magazin.testing
import zope.component


class PreviewURLTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.magazin.testing.LAYER

    def test_zmo_content_gets_different_url(self):
        content = self.repository['magazin']['test'] = ExampleContentType()
        self.assertEqual(
            'http://localhost/zmo-preview-prefix/magazin/test',
            zope.component.getMultiAdapter(
                (content, 'preview'),
                zeit.cms.browser.interfaces.IPreviewURL))
