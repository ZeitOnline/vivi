# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import persistent
import re
import zope.app.testing.functional
import zope.testing.renormalizing


ObjectLogLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ObjectLogLayer', allow_teardown=True)


FORMATTED_DATE_REGEX = re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d')
checker = zope.testing.renormalizing.RENormalizing([
    (FORMATTED_DATE_REGEX, '<formatted date>')])


class Content(persistent.Persistent):
    pass
