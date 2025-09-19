"""Module to parse embedded image informationen"""

from PIL import Image, ImageCms, IptcImagePlugin
from PIL.ExifTags import TAGS
import opentelemetry.trace


def exif(img: Image) -> dict:
    metadata = {}
    for tag_id, value in img.getexif().items():
        tag_name = TAGS.get(tag_id, tag_id)
        metadata[tag_name] = value
    return metadata


def icc(icc_profile: ImageCms.ImageCmsProfile) -> dict:
    """List available and useful properties from the icc profile
    https://pillow.readthedocs.io/en/stable/reference/ImageCms.html#cmsprofile"""
    metadata = {}
    for prop_name in dir(ImageCms.core.CmsProfile):
        if prop_name.startswith('_'):
            continue
        try:
            value = getattr(icc_profile.profile, prop_name, None)
            if value is not None and not callable(value):
                if hasattr(value, '__str__'):
                    metadata[prop_name] = str(value)
                else:
                    metadata[prop_name] = value
        except Exception:
            # too many available image sources and we cannot check them all
            continue
    return metadata


def iptc(img: Image) -> dict:
    """Pillows IPTC parser doesn't know when to stop.
    After reading all IPTC records, it continues reading
    and if it encounters other blocks it will throw an exception.

    See https://de.wikipedia.org/wiki/IPTC-IIM-Standard for a list of available iptc tags"""
    iptc_tags = {(2, 110): 'copyright', (2, 120): 'caption', (2, 105): 'title'}
    metadata = {}
    try:
        iptc = IptcImagePlugin.getiptcinfo(img)
    except SyntaxError as err:
        current_span = opentelemetry.trace.get_current_span()
        current_span.record_exception(err)
    else:
        if isinstance(iptc, dict):
            for code, value in iptc.items():
                tag_name = iptc_tags.get(code, code)
                metadata[tag_name] = value

    return metadata
