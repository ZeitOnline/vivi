import zeit.content.animation.animation
import zeit.content.animation.testing


class AnimationTest(zeit.content.animation.testing.FunctionalTestCase):

    def test_article_reference(self):
        article = self.article
        animation = zeit.content.animation.animation.Animation()
        animation.article = article
        assert animation.title == article.title

    def test_display_mode(self):
        animation = zeit.content.animation.animation.Animation()
        animation.display_mode = 'images'
        assert animation.display_mode == 'images'
