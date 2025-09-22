import pytest
import transaction

from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
from zeit.content.article.interfaces import ISpeechbertChecksum
from zeit.content.audio.interfaces import IAudioReferences
from zeit.content.image.interfaces import IImages
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

    def test_delegates_IImages_to_article(self):
        image = ICMSContent('http://xml.zeit.de/image1')
        with checked_out(self.repository['article']) as co:
            IImages(co).image = image
        transaction.commit()
        animation = zeit.content.animation.animation.Animation()
        animation.article = self.repository['article']
        self.assertEqual(image, IImages(animation).image)

    def test_delegates_IAudio_to_article(self):
        self.repository['audio'] = zeit.content.audio.audio.Audio()
        audio = self.repository['audio']
        with checked_out(self.repository['article']) as co:
            IAudioReferences(co).add(audio)
        transaction.commit()
        animation = zeit.content.animation.animation.Animation()
        animation.article = self.repository['article']
        self.assertEqual((audio,), IAudioReferences(animation).items)

    def test_delegates_ISpeechbert_to_article(self):
        ISpeechbertChecksum(self.repository['article']).checksum = 'foo'
        animation = zeit.content.animation.animation.Animation()
        animation.article = self.repository['article']
        self.assertEqual('foo', ISpeechbertChecksum(animation).checksum)
