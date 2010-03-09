# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import pybrightcove.connection
import zeit.cms.testing
import zope.app.testing.functional

product_config = """\
<product-config zeit.brightcove>
</product-config>
"""


VIDEO_1234 = {
    'items': [
        {'creationDate': '1268018138802',
         'customFields': {
             'ressort': 'Auto',
             'newsletter': '1',
             'breaking-news': '0',
             'cmskeywords': 'Politik;koalition',
         },
         'economics': 'AD_SUPPORTED',
         'id': 70662056001L,
         'lastModifiedDate': '1268053197824',
         'length': 152640,
         'linkText': None,
         'linkURL': None,
         'longDescription': u'Mehr Glanz, Glamour und erwartungsvolle Spannung',
         'name': 'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung',
         'playsTotal': None,
         'playsTrailingWeek': None,
         'publishedDate': '1268053197823',
         'referenceId': '2010-03-08T023523Z_1_OVE6276PP_RTRMADC_0_ONLINE',
         'shortDescription': u'Glanz, Glamour und erwartungsvolle Spannung',
         'tags': ['Vermischtes'],
         'thumbnailURL': 'http://thumbnailurl',
         'videoStillURL': 'http://videostillurl'}
    ],
    'page_number': 0,
    'page_size': 0,
    'total_count': -1,
}


class APIConnection(pybrightcove.connection.APIConnection):

    posts = []

    def get_list(self, command, item_class, page_size, page_number, sort_by,
                 sort_order, **kwargs):

        if (command == 'find_videos_by_ids' and
            kwargs.get('video_ids') == '1234'):
            result = VIDEO_1234
        else:
            result = {"items": [None],
                      "page_number": 0,
                      "page_size": 0,
                      "total_count": -1}
        return pybrightcove.connection.ItemCollection(data=result,
                                                      item_class=item_class,
                                                      connection=self)

    def post(self, command, file_to_upload=None, **kwargs):
        self.posts.append((command, file_to_upload, kwargs))


BrightcoveLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'BrightcoveLayer', allow_teardown=True,
    product_config=product_config)



class BrightcoveTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = BrightcoveLayer

    def tearDown(self):
        APIConnection.posts[:] = []
        super(BrightcoveTestCase, self).tearDown()


# 70355221001
# 70740054001
# 70662056001
# 70355162001

