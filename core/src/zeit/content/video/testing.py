import doctest
import pkg_resources
import plone.testing
import zeit.cms.repository.folder
import zeit.cms.testing
import zeit.push
import zeit.solr.testing
import zeit.workflow.testing


product_config = """\
<product-config zeit.content.video>
    source-serie file://{0}
</product-config>
""".format(
    pkg_resources.resource_filename(__name__, 'tests/serie.xml'))


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(
        zeit.push.product_config +
        zeit.cms.testing.cms_product_config +
        zeit.solr.testing.product_config +
        zeit.workflow.testing.product_config +
        product_config))


LAYER = plone.testing.Layer(
    bases=(ZCML_LAYER, zeit.solr.testing.SOLR_MOCK_LAYER),
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
