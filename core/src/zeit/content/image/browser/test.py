# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import os
import re
import unittest

from zope.testing import doctest
import zope.testing.renormalizing

import zeit.cms.testing
import zeit.content.image.test

now_plus_7_days = datetime.date.today() + datetime.timedelta(days=7)

checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('%04d-%02d-%02d 00:00:00' % (
        now_plus_7_days.year, now_plus_7_days.month, now_plus_7_days.day)),
     '<Datetime-7-Days-In-Future>')])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'copyright.txt',
        'imagefolder.txt',
        checker=checker,
        layer=zeit.content.image.test.ImageLayer))
    return suite
