from lxml.builder import E

from zeit.content.animation.animation import Animation
from zeit.content.article.article import Article
from zeit.content.article.edit.animation import Animation as AnimatedHeader
from zeit.content.article.testing import MOCK_LAYER, FunctionalTestCase
from zeit.content.video.video import Video


class TestAnimation(FunctionalTestCase):
    layer = MOCK_LAYER

    def test_animation(self):
        self.repository['article'] = Article()
        self.repository['video'] = Video()
        animation = Animation()
        animation.article = self.repository['article']
        animation.video = self.repository['video']
        self.repository['animation'] = animation
        node = E.animation()
        E.tree(node)
        animatedheader = AnimatedHeader(None, node)
        animatedheader.animation = self.repository['animation']
        assert animatedheader.xml.get('href') == 'http://xml.zeit.de/animation'
