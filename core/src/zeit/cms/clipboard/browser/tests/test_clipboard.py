from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.clipboard.browser.clipboard
import zeit.cms.clipboard.interfaces
import zeit.cms.testing


class ClipboardTest(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super().setUp()
        self.clipboard = zeit.cms.clipboard.interfaces.IClipboard(
            self.principal)
        UNUSED_REQUEST = None
        self.view = zeit.cms.clipboard.browser.clipboard.Tree(
            self.clipboard, UNUSED_REQUEST)

    def test_get_type_of_content_object(self):
        folder = self.clipboard.addClip('Favoriten')
        self.repository['test'] = ExampleContentType()
        content = self.repository['test']
        self.clipboard.addContent(folder, content, 'testname', insert=True)
        clip = list(folder.values())[0]
        self.assertEqual('testcontenttype', self.view.getType(clip))

    def test_get_type_of_clip_is_empty_string(self):
        folder = self.clipboard.addClip('Favoriten')
        self.assertEqual('', self.view.getType(folder))
