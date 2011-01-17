# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import pytz
import zeit.cms.interfaces
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zeit.wysiwyg.html
import zope.component
import zope.interface


WYSIWYGLayer = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


class WYSIWYGTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = WYSIWYGLayer


class HTMLContent(zeit.wysiwyg.html.HTMLContentBase):

    zope.component.adapts(
        zeit.cms.testcontenttype.interfaces.ITestContentType)

    def get_tree(self):
        return self.context.xml['body']


VIDEO1 = 'http://video.zeit.de/video/1'
VIDEO2 = 'http://video.zeit.de/video/2'
VIDEO3 = 'http://video.zeit.de/video/3'
PLAYLIST = 'http://video.zeit.de/playlist/1'


class Dummy(object):
    pass


@zope.component.adapter(basestring)
@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
def mock_video_repository(uniqueId):
    result = None
    if uniqueId == VIDEO1:
        result = Dummy()
        result.expires = datetime.datetime(2010, 1, 1, tzinfo=pytz.UTC)
    elif uniqueId == VIDEO2:
        result = Dummy()
        result.expires = datetime.datetime(2009, 1, 1, tzinfo=pytz.UTC)
    elif uniqueId == VIDEO3:
        result = Dummy()
        result.expires = None
    elif uniqueId == PLAYLIST:
        result = Dummy()
    return result
