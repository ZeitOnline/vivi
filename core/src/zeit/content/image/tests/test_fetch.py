import importlib.resources
import zeit.content.image.testing
import shutil
import requests
from os import path
from zeit.content.image import image


class TestImageServing(zeit.content.image.testing.StaticBrowserTestCase):
    def setUp(self):
        image_dir = importlib.resources.files(
            "zeit.content.image.browser") / "testdata"
        shutil.copytree(image_dir, path.join(self.layer["documentroot"], "testdata"))

    def test_image_server(self):
        response = requests.get(
            "http://{0.layer[http_address]}/testdata/opernball.jpg".format(self)
        )
        assert response.status_code == 200

    def test_fetch_remote_image(self):
        local_image = image.get_remote_image(
            "http://{0.layer[http_address]}/testdata/opernball.jpg".format(self)
        )
        assert local_image.mimeType == "image/jpeg"
        assert local_image.__name__ == "opernball.jpg"

    def test_fetch_remote_image_fail(self):
        local_image = image.get_remote_image(
            "http://{0.layer[http_address]}/testdata/nosuchimage.jpg".format(self)
        )
        assert local_image is None

    def test_fetch_remote_image_fail_url(self):
        local_image = image.get_remote_image("nosuchhost")
        assert local_image is None
