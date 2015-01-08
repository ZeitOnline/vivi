import collections
import zc.sourcefactory.basic


class MediaTypeSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return ['audio', 'video']


class FormatSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return ['small', 'with-links', 'large']


class PlayerSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = collections.OrderedDict((
        (u'vid', u'Einzelvideo'),
        (u'pls', u'Playlist'),
    ))

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]
