import zeit.content.article.testing


class GenreTest(zeit.content.article.testing.FunctionalTestCase):
    def test_find_byline(self):
        source = zeit.content.article.interfaces.IArticle['genre'].source(None)
        self.assertEqual(None, source.byline('nonexistent'))
        self.assertEqual(None, source.byline('nachricht'))
        self.assertEqual('Eine Glosse von', source.byline('glosse'))

    def test_find_audio(self):
        source = zeit.content.article.interfaces.IArticle['genre'].source(None)
        self.assertEqual(None, source.audio('nonexistent'))
        self.assertEqual(None, source.audio('bericht'))
        self.assertEqual('speechbert', source.audio('nachricht'))

    def test_find_feedback(self):
        source = zeit.content.article.interfaces.IArticle['genre'].source(None)
        self.assertEqual(None, source.feedback('nonexistent'))
        self.assertEqual(None, source.feedback('nachricht'))
        self.assertEqual('Hat Ihnen diese Glosse gefallen?', source.feedback('glosse'))
