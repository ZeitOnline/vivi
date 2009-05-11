# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.sourcefactory.basic


class MediaTypeSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return ['audio', 'video']


class FormatSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return ['small', 'with-links', 'large']
