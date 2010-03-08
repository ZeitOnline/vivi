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


SINGLE_RESULT = {'items': [{'thumbnailURL': 'http://brightcove.vo.llnwd.net/d10/unsecured/media/18140073001/18140073001_70700928001_th-70700004001.jpg?pubId=18140073001', 'name': 'Starrummel auf dem Roten Teppich zur 82. Oscar-Verleihung', 'publishedDate': '1268053197823', 'linkURL': None, 'lastModifiedDate': '1268053197824', 'tags': ['Vermischtes'], 'longDescription': u'Glanz, Glamour und erwartungsvolle Spannung lag \xfcber den Roten Teppich am Kodak Theatre in Los Angeles kurz vor der 82. Oscar-Verleihung.', 'playsTotal': None, 'length': 152640, 'referenceId': '2010-03-08T023523Z_1_OVE6276PP_RTRMADC_0_ONLINE-OSCARS-TEPPICH-O', 'playsTrailingWeek': None, 'linkText': None, 'economics': 'AD_SUPPORTED', 'creationDate': '1268018138802', 'shortDescription': u'Glanz, Glamour und erwartungsvolle Spannung lag \xfcber den Roten Teppich am Kodak Theatre in Los Angeles kurz vor der 82. Oscar-Verleihung.', 'id': 70662056001L, 'videoStillURL': 'http://brightcove.vo.llnwd.net/d10/unsecured/media/18140073001/18140073001_70700927001_vs-70700004001.jpg?pubId=18140073001'}], 'page_number': 0, 'page_size': 0, 'total_count': -1}


class APIConnection(pybrightcove.connection.APIConnection):

    def get_list(self, command, item_class, page_size, page_number, sort_by,
                 sort_order, **kwargs):

        if (command == 'find_videos_by_ids' and
            kwargs.get('video_ids') == '1234'):
            result = SINGLE_RESULT
        else:
            result = {}
        return pybrightcove.connection.ItemCollection(data=result,
                                                      item_class=item_class,
                                                      connection=self)


BrightcoveLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'BrightcoveLayer', allow_teardown=True,
    product_config=product_config)



class BrightcoveTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = BrightcoveLayer

# 70355221001
# 70740054001
# 70662056001
# 70355162001

