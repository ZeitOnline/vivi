import requests
from zeit.content.image.image import LocalImage

KiB = 1024
DOWNLOAD_CHUNK_SIZE = 2 * KiB


def get_remote_image(url, timeout=2):

    response = requests.get(url, stream=True, timeout=timeout)
    image = LocalImage()
    with image.open('w') as fh:
        first_chunk = True
        for chunk in response.iter_content(DOWNLOAD_CHUNK_SIZE):
            # Too small means something is not right with this download
            if first_chunk:
                first_chunk = False
                assert len(chunk) > DOWNLOAD_CHUNK_SIZE / 2
            fh.write(chunk)
    return image
