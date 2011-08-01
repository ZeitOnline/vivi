# coding: utf8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2
import zeit.cms.testing
import zeit.content.article.testing


class CheckinTest(zeit.content.article.testing.SeleniumTestCase):

    def setUp(self):
        super(CheckinTest, self).setUp()
        self.open('/repository/online/2007/01/Somalia/')
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=checkin')

    def test_article_should_be_checked_in(self):
        s = self.selenium
        s.clickAndWait('id=checkin')
        s.assertElementNotPresent('id=checkin')
