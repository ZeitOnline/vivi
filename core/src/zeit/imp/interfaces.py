# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt


import zope.interface
import zope.schema


class ICropper(zope.interface.Interface):
    """Crop master image in an image group."""

    def crop(w, h, x1, y1, x2, y2, name, border=False):
        """Crop master image from image group.

        - The master image is first scaled to w, h.
        - From the resulting image the box x1, y2; x2, y2 is cropped.
        - If border is true a 1px solid black border is painted inside the
          cropped image.
        - The cropped image is put into the image group as
          <group-name>-<name>.jpg

        returns the cropped image.

        """


class IPossibleScale(zope.interface.Interface):

    name = zope.interface.Attribute("Name in folder")
    width = zope.interface.Attribute(
        "Width, leading ? indicates variable width.")
    height = zope.interface.Attribute(
        "height, leading ? indicates variable height.")
    title = zope.schema.TextLine(title=u'Title')
