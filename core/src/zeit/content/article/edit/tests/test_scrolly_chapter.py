import lxml.builder
import zope.component

import zeit.content.article.article
import zeit.content.article.edit.body
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.content.image.testing
import zeit.edit.interfaces


class ScrollyChapterTest(zeit.content.article.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.article = zeit.content.article.article.Article()
        self.body = zeit.content.article.edit.body.EditableBody(
            self.article, self.article.xml.find('body')
        )

    def create_scrolly_chapter(self):
        factory = zope.component.getAdapter(
            self.body, zeit.edit.interfaces.IElementFactory, 'scrolly_chapter'
        )
        return factory()

    def test_factory_should_create_scrolly_chapter_node(self):
        chapter = self.create_scrolly_chapter()
        self.assertTrue(zeit.content.article.edit.interfaces.IScrollyChapter.providedBy(chapter))
        self.assertEqual('scrolly_chapter', chapter.xml.tag)

    def test_kicker_attribute_should_be_stored_in_xml(self):
        from zeit.content.article.edit.scrolly_chapter import ScrollyChapter

        chapter = ScrollyChapter(None, lxml.builder.E.scrolly_chapter())
        kicker = 'Chapter One'
        chapter.kicker = kicker
        self.assertEqual(kicker, chapter.kicker)
        self.assertEqual(kicker, chapter.xml.get('kicker'))

    def test_title_attribute_should_be_stored_in_xml(self):
        from zeit.content.article.edit.scrolly_chapter import ScrollyChapter

        chapter = ScrollyChapter(None, lxml.builder.E.scrolly_chapter())
        title = 'The Beginning'
        chapter.title = title
        self.assertEqual(title, chapter.title)
        self.assertEqual(title, chapter.xml.get('title'))

    def test_font_style_attribute_should_be_stored_in_xml(self):
        from zeit.content.article.edit.scrolly_chapter import ScrollyChapter

        chapter = ScrollyChapter(None, lxml.builder.E.scrolly_chapter())
        font_style = 'tiemann'
        chapter.font_style = font_style
        self.assertEqual(font_style, chapter.font_style)
        self.assertEqual(font_style, chapter.xml.get('font-style'))

    def test_font_style_default_should_be_tablet_gothic(self):
        chapter = self.create_scrolly_chapter()
        self.assertEqual('tablet-gothic', chapter.font_style)

    def test_references_should_accept_image_group(self):
        chapter = self.create_scrolly_chapter()
        image = self.repository['2006']['DSC00109_2.JPG']
        chapter.references = image
        self.assertEqual(image.uniqueId, chapter.xml.get('href'))

    def test_references_should_be_retrievable(self):
        chapter = self.create_scrolly_chapter()
        image = self.repository['2006']['DSC00109_2.JPG']
        chapter.references = image
        self.assertEqual(image, chapter.references)

    def test_factory_title_should_be_scrollytelling_chapter(self):
        factory = zope.component.getAdapter(
            self.body, zeit.edit.interfaces.IElementFactory, 'scrolly_chapter'
        )
        self.assertEqual('Scrollytelling Chapter', factory.title)
