# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import re
import zope.testing.renormalizing


product_config = {'zeit.content.cp': {'rules-url': 'file://%s' % pkg_resources.resource_filename(
            'zeit.content.cp.tests', 'rule_testdata.py')}}

layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'zeit.content.cp.tests.layer', allow_teardown=True)


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>"),
    (re.compile('0x[0-9a-f]+'), "0x..."),
])
