# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing


TodayLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'TodayLayer', allow_teardown=True)

today_xml_url = 'file://%s' % os.path.join(
    os.path.dirname(__file__), 'today.xml')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'yesterday.txt',
        layer=TodayLayer,
        product_config={'zeit.today': {'today-xml-url': today_xml_url}}
    ))
    return suite
