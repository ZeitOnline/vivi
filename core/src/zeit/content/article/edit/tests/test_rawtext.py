import zeit.content.article.testing


class RawTextTest(zeit.content.article.testing.FunctionalTestCase):

    def get_rawtext(self):
        from zeit.content.article.edit.rawtext import RawText
        import lxml.objectify
        rawtext = RawText(None, lxml.objectify.E.rawtext())
        return rawtext

    def test_rawtext_should_be_set(self):
        rawtext = self.get_rawtext()
        rawtext.text = u'my_text'
        self.assertEqual(u'my_text', rawtext.xml.xpath('text')[0])


class TestFactory(zeit.content.article.testing.FunctionalTestCase):

    def test_factory_should_create_rawtext_node(self):
        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces
        import zope.component
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, 'rawtext')
        self.assertEqual('Raw text block', factory.title)
        div = factory()
        self.assertTrue(
            zeit.content.article.edit.interfaces.IRawText.providedBy(div))
        self.assertEqual('rawtext', div.xml.tag)
