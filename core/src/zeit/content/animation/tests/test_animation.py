from zeit.cms.interfaces import ICMSContent
import zeit.content.animation.animation
import zeit.content.animation.testing
import zeit.content.video.testing


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

    def test_image_references(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        image2 = ICMSContent('http://xml.zeit.de/2006/DSC00109_3.JPG')
        article = self.article
        animation = zeit.content.animation.animation.Animation()
        animation.article = article
        animation.images = (image, image2)
        assert len(animation.xml.body.image) == 2
        assert animation.xml.body.image[0].xpath('@type')[0] == 'JPG'

    def test_genre_attribute(self):
        article = self.article
        animation = zeit.content.animation.animation.Animation()
        animation.article = article
        assert animation.genre == article.genre
