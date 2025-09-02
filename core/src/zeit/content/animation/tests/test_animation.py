import pytest

from zeit.cms.interfaces import ICMSContent
import zeit.content.animation.animation
import zeit.content.animation.testing
import zeit.content.video.testing


@pytest.mark.parametrize('display_mode', ['images', 'gallery-manual'])
def test_display_mode(display_mode):
    animation = zeit.content.animation.animation.Animation()
    animation.display_mode = display_mode
    assert animation.display_mode == display_mode


class AnimationTest(zeit.content.animation.testing.FunctionalTestCase):
    def test_article_reference(self):
        article = self.repository['article']
        animation = zeit.content.animation.animation.Animation()
        animation.article = article
        assert animation.title == article.title

    def test_image_references(self):
        image1 = ICMSContent('http://xml.zeit.de/image1')
        image2 = ICMSContent('http://xml.zeit.de/image2')
        article = self.repository['article']
        animation = zeit.content.animation.animation.Animation()
        animation.article = article
        animation.images = (image1, image2)
        assert len(animation.xml.findall('body/image')) == 2
        assert animation.xml.find('body/image').get('type') == 'jpeg'

    def test_genre_attribute(self):
        article = self.repository['article']
        animation = zeit.content.animation.animation.Animation()
        animation.article = article
        assert animation.genre == article.genre
