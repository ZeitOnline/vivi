import lxml.objectify
import mock
import zeit.content.modules.embed
import zeit.content.modules.testing


class RecipeListTest(zeit.content.modules.testing.FunctionalTestCase):

    def setUp(self):
        super(RecipeListTest, self).setUp()
        self.context = mock.Mock()
        self.context.__parent__ = None
        self.module = zeit.content.modules.recipelist.RecipeList(
            self.context, lxml.objectify.XML('<container/>'))

    def test_title_should_be_stored_in_xml(self):
        self.module.title = 'banana'
        self.assertEqual(self.module.xml.xpath('//title'), ['banana'])
