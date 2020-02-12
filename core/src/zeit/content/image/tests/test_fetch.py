import pytest
import shutil
from os import path
from pytest_server_fixtures.http import SimpleHTTPTestServer
from zeit.content.image import fetch
import zeit.cms.repository.interfaces
import zope.component
import zeit.content.image.testing


@pytest.yield_fixture
def image_server():
    image_dir = path.abspath(path.join(path.dirname(__file__), '..', 'browser', 'testdata'))
    with SimpleHTTPTestServer() as s:
        shutil.copytree(image_dir, path.join(s.document_root, "testdata"))
        s.start()
        yield s


def test_image_server(image_server):
    response = image_server.get('/testdata/opernball.jpg')
    assert response.status_code == 200


def test_fetch_remote_image(image_server):
    local_image = fetch.get_remote_image('%s/testdata/opernball.jpg' % image_server.uri)
    assert local_image.mimeType == 'image/jpeg'


def test_fetch_remote_image_fail(image_server):
    local_image = fetch.get_remote_image('%s/testdata/nosuchimage.jpg' % image_server.uri)
    assert local_image is None


class ImageGroupTest(zeit.content.image.testing.FunctionalTestCase):

    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def test_image_group_from_image(self):
        repository = self.repository()
        local_image = zeit.content.image.testing.create_local_image('opernball.jpg')
        group = fetch.image_group_from_image(repository, 'group', local_image)
        assert group.master_image is not None

    def test_image_group_from_none(self):
        repository = self.repository()
        group = fetch.image_group_from_image(repository, 'group', None)
        assert group.master_image is None
