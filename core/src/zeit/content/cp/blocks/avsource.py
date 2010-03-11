# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import stabledict
import zc.sourcefactory.basic


class MediaTypeSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return ['audio', 'video']


class FormatSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return ['small', 'with-links', 'large']


class PlayerSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = stabledict.StableDict((
        (u'vid', u'Einzelvideo'),
        (u'pls', u'Playlist'),
    ))

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]
