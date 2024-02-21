import lxml.builder
import zope.component

import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.edit.interfaces


class DivisionTest(zeit.content.article.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.article = zeit.content.article.article.Article()
        self.body = zeit.content.article.edit.body.EditableBody(
            self.article, self.article.xml.find('body')
        )

    def create_division(self):
        factory = zope.component.getAdapter(
            self.body, zeit.edit.interfaces.IElementFactory, 'division'
        )
        return factory()

    def test_teaser_attribute_should_be_added_to_xml(self):
        from zeit.content.article.edit.division import Division

        div = Division(None, lxml.builder.E.division())
        teaser = 'My div teaser'
        div.teaser = teaser
        self.assertEqual(teaser, div.teaser)
        self.assertEqual(teaser, div.xml.get('teaser'))

    def test_factory_should_create_div_node_with_type(self):
        div = self.create_division()
        self.assertTrue(zeit.content.article.edit.interfaces.IDivision.providedBy(div))
        self.assertEqual('division', div.xml.tag)
        self.assertEqual('page', div.xml.get('type'))

    def test_page_number_counts_divisions(self):
        para = zope.component.getAdapter(self.body, zeit.edit.interfaces.IElementFactory, 'p')
        para()
        para()
        div = self.create_division()
        # one division is always present, which gets number 0
        self.assertEqual(1, div.number)
