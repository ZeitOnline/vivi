import zope.component

import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.edit.interfaces


class RawTextTest(zeit.content.article.testing.FunctionalTestCase):
    def get_rawtext(self):
        import lxml.objectify

        from zeit.content.article.edit.rawtext import RawText

        rawtext = RawText(None, lxml.objectify.E.rawtext())
        return rawtext

    def test_rawtext_should_be_set(self):
        rawtext = self.get_rawtext()
        rawtext.text = 'my_text'
        self.assertEqual('my_text', rawtext.xml.xpath('text')[0])

    def test_each_module_should_use_its_own_parameters(self):
        article = zeit.content.article.article.Article()
        m1 = article.body.create_item('rawtext')
        m2 = article.body.create_item('rawtext')
        m1.params['foo'] = 'bar'
        m2.params['foo'] = 'qux'
        self.assertEqual('bar', m1.params['foo'])
        self.assertEqual('qux', m2.params['foo'])


class TestFactory(zeit.content.article.testing.FunctionalTestCase):
    def test_factory_should_create_rawtext_node(self):
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(article, article.xml.body)
        factory = zope.component.getAdapter(body, zeit.edit.interfaces.IElementFactory, 'rawtext')
        self.assertEqual('Raw text block', factory.title)
        div = factory()
        self.assertTrue(zeit.content.article.edit.interfaces.IRawText.providedBy(div))
        self.assertEqual('rawtext', div.xml.tag)
