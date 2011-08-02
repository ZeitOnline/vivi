# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.testcontenttype.testcontenttype import TestContentType
import zeit.cms.clipboard.browser.clipboard
import zeit.cms.clipboard.interfaces
import zeit.cms.testing


class ClipboardTest(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(ClipboardTest, self).setUp()
        self.clipboard = zeit.cms.clipboard.interfaces.IClipboard(
            self.principal)
        UNUSED_REQUEST = None
        self.view = zeit.cms.clipboard.browser.clipboard.Tree(
            self.clipboard, UNUSED_REQUEST)

    def test_get_type_of_content_object(self):
        folder = self.clipboard.addClip('Favoriten')
        self.repository['test'] = TestContentType()
        content = self.repository['test']
        self.clipboard.addContent(folder, content, 'testname',
            insert=True)
        clip = list(folder.values())[0]
        self.assertEqual('testcontenttype', self.view.getType(clip))

    def test_get_type_of_clip_is_empty_string(self):
        folder = self.clipboard.addClip('Favoriten')
        self.assertEqual('', self.view.getType(folder))
