# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt


import zope.interface
import zope.schema


class ICropper(zope.interface.Interface):
    """Crop master image in an image group."""

    downsample_filter = zope.interface.Attribute(
        'Downsample filter to use: ANTIALIAS, NEAREST, ...')

    def add_filter(name, factor):
        """Add a filter which is applied before crop.

        name: one of brightnes, contrast, color, sharpness
        factor: float 0..1000, 1 meaning no change.

        raises ValueError if there is no filter for given name.

    """

    def crop(w, h, x1, y1, x2, y2, border=False):
        """Crop master image from image group.

        - The master image is first scaled to w, h.
        - From the resulting image the box x1, y2; x2, y2 is cropped.
        - If border is true a 1px solid black border is painted inside the
          cropped image.

        returns the cropped image (PIL.Image.Image instance).

        """

    def store(name):
        """Store a previously cropped image.

        - The cropped image is put into the image group as
          <group-name>-<name>.jpg

        raises RuntimeError when crop() was note called before.
        returns image

        """


class IPossibleScale(zope.interface.Interface):

    name = zope.interface.Attribute("Name in folder")
    width = zope.interface.Attribute(
        "Width, leading ? indicates variable width.")
    height = zope.interface.Attribute(
        "height, leading ? indicates variable height.")
    title = zope.schema.TextLine(title=u'Title')
