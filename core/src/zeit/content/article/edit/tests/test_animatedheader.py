from lxml.objectify import E
from zeit.content.animation.animation import Animation
from zeit.content.article.article import Article
from zeit.content.article.edit.animatedheader import AnimatedHeader
from zeit.content.article.testing import FunctionalTestCase, MOCK_LAYER
from zeit.content.video.video import Video


class TestAnimatedHeader(FunctionalTestCase):

    layer = MOCK_LAYER

    def test_animatedheader(self):
        self.repository['article'] = Article()
        self.repository['video'] = Video()
        animation = Animation()
        animation.article = self.repository['article']
        animation.video = self.repository['video']
        self.repository['animation'] = animation
        animatedheader = AnimatedHeader(None, E.animatedheader())
        animatedheader.animation = self.repository['animation']
        assert animatedheader.xml.get('href') == 'http://xml.zeit.de/animation'
