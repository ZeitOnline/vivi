from zeit.content.article.edit.animatedheader import AnimatedHeader
import lxml.objectify
import zeit.content.animation.animation
import zeit.content.article.testing
import zeit.content.article.article
import zeit.content.video.video


class TestAnimatedHeader(zeit.content.article.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.MOCK_LAYER

    def test_animatedheader(self):
        self.repository['article'] = zeit.content.article.article.Article()
        self.repository['video'] = zeit.content.video.video.Video()
        animation = zeit.content.animation.animation.Animation()
        animation.article = self.repository['article']
        animation.video = self.repository['video']
        self.repository['animation'] = animation
        animatedheader = AnimatedHeader(None, lxml.objectify.E.animatedheader())
        animatedheader.animation = self.repository['animation']
        assert animatedheader.xml.get('href') == 'http://xml.zeit.de/animation'
