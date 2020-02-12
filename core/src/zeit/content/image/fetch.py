import requests
from zeit.content.image.image import LocalImage
from zeit.content.image.imagegroup import ImageGroup

KiB = 1024
DOWNLOAD_CHUNK_SIZE = 2 * KiB

# both of these helpers are very defensive and are eager not to
# fail (but return None instead) because we want to have empty
# imagegroups in that case (so that they can be manipulated by
# editors, if need be)


def get_remote_image(url, timeout=2):

    try:
        response = requests.get(url, stream=True, timeout=timeout)
    except Exception:
        return
    if not response.ok:
        return
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


def image_group_from_image(where, name, image):
    group = ImageGroup()
    if image is not None:
        image_name = 'master.' + image.format
        group.master_images = (('desktop', image_name))
    where[name] = group
    if image is not None:
        where[name][image_name] = image
    return where[name]
