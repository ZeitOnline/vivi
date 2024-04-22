import datetime

import pytz
import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zeit.content.image.testing
import zeit.wysiwyg.html


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(zeit.content.image.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


@zope.component.adapter(zeit.cms.testcontenttype.interfaces.IExampleContentType)
class HTMLContent(zeit.wysiwyg.html.HTMLContentBase):
    def get_tree(self):
        return self.context.xml.find('body')


VIDEO1 = 'http://video.zeit.de/video/1'
VIDEO2 = 'http://video.zeit.de/video/2'
VIDEO3 = 'http://video.zeit.de/video/3'


class Dummy:
    pass


@zope.component.adapter(str)
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
    return result
