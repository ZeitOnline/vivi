import doctest
import mock
import plone.testing
import zeit.cms.repository.folder
import zeit.cms.testing
import zeit.find.testing
import zeit.push.testing
import zeit.solr.testing
import zeit.workflow.testing
import zope.component
import zope.interface


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(
        zeit.find.testing.product_config +
        zeit.push.testing.product_config +
        zeit.cms.testing.cms_product_config +
        zeit.solr.testing.product_config +
        zeit.workflow.testing.product_config))

PUSH_LAYER = zeit.push.testing.UrbanairshipTemplateLayer(
    name='UrbanairshipTemplateLayer', bases=(ZCML_LAYER,))


class PlayerMockLayer(plone.testing.Layer):

    def setUp(self):
        self['player'] = mock.Mock()
        zope.interface.alsoProvides(
            self['player'], zeit.content.video.interfaces.IPlayer)
        zope.component.getSiteManager().registerUtility(self['player'])

    def tearDown(self):
        zope.component.getSiteManager().unregisterUtility(self['player'])

    def testSetUp(self):
        self['player'].reset_mock()
        self['player'].get_video.return_value = {
            'renditions': (),
            'thumbnail': None,
            'video_still': None,
        }

PLAYER_MOCK_LAYER = PlayerMockLayer()


LAYER = plone.testing.Layer(
    bases=(PUSH_LAYER, zeit.solr.testing.SOLR_MOCK_LAYER, PLAYER_MOCK_LAYER),
    name='Layer', module=__name__)


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = LAYER


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', LAYER)
    kw['package'] = doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


def playlist_factory(self, location=''):
    from zeit.content.video.playlist import Playlist
    parent = self.repository
    with zeit.cms.testing.site(self.getRootFolder()):
        with zeit.cms.testing.interaction():
            playlist = Playlist()
            yield playlist
            for name in location.split('/'):
                if not name:
                    continue
                if name not in parent:
                    parent[name] = zeit.cms.repository.folder.Folder()
                parent = parent[name]
            parent['pls'] = playlist
    yield parent['pls']


def video_factory(self):
    from zeit.content.video.video import Video
    with zeit.cms.testing.site(self.getRootFolder()):
        with zeit.cms.testing.interaction():
            video = Video()
            yield video
            self.repository['video'] = video
    yield self.repository['video']
