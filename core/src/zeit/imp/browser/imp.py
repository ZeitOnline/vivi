# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt


class Imp(object):

    @property
    def width(self):
        return self.context.getImageSize()[0]

    @property
    def height(self):
        return self.context.getImageSize()[1]
