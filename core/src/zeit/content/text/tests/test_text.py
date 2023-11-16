from zeit.content.text.interfaces import IText
from zeit.content.text.text import Text
from zope.interface.verify import verifyObject
import zeit.cms.interfaces
import zeit.content.text.testing


class TextTest(zeit.content.text.testing.FunctionalTestCase):
    def test_interfaces(self):
        text = Text()
        text.text = 'foo'
        self.assertEqual('foo', text.text)
        self.assertTrue(verifyObject(IText, text))
        self.assertTrue(verifyObject(zeit.cms.interfaces.IAsset, text))

    def test_can_be_added_to_repository(self):
        text = Text()
        text.text = 'foo'
        self.assertEqual('foo', text.text)
        self.repository['mytext'] = text
        text = self.repository['mytext']
        self.assertEqual('foo', text.text)
