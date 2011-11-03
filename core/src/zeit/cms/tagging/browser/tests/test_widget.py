# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.cms.testing

import unittest2 as unittest


class TestWidget(zeit.cms.testing.SeleniumTestCase):

    def get_tag(self, code):
        tag = mock.Mock()
        tag.code = tag.label = unicode(code)
        tag.disabled = False
        return tag

    def setup_tags(self, *codes):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                with zeit.cms.checkout.helper.checked_out(
                    self.repository['testcontent']) as co:
                    co.keywords = tuple(self.get_tag(code) for code in codes)

    def open_content(self):
        self.open('/repository/testcontent/@@checkout')
        s = self.selenium
        s.type('name=form.year', '2011')
        s.select('name=form.ressort', 'label=Deutschland')
        s.type('name=form.title', 'Test')
        s.type('name=form.authors.0.', 'Hans Wurst')

    def test_tags_should_be_sortable(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.assertTextPresent('t1*t2*t3*t4')
        s.dragAndDropToObject(
            "xpath=//li[contains(., 't1')]",
            "xpath=//li[contains(., 't3')]")
        s.assertTextPresent('t2*t3*t1*t4')

    def test_sorted_tags_should_be_saved(self):
        tags = self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.dragAndDropToObject(
            "xpath=//li[contains(., 't1')]",
            "xpath=//li[contains(., 't3')]")
        s.assertTextPresent('t2*t3*t1*t4')
        s.clickAndWait('name=form.actions.apply')
        s.clickAndWait('link=Checkin*')
        self.assertEqual(
            ['t2', 't3', 't1', 't4'],
            [tag.code for tag in self.repository['testcontent'].keywords])

    def test_unchecked_tags_should_be_disabled(self):
        tags = self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.click("xpath=//li/label[contains(., 't1')]")
        s.clickAndWait('name=form.actions.apply')
        s.clickAndWait('link=Checkin*')
        self.assertEqual(
            ['t2', 't3', 't4'],
            [tag.code for tag in self.repository['testcontent'].keywords])
        self.assertEqual(
            ['t1'],
            [tag.code
             for tag in self.repository['testcontent'].disabled_keywords])

    def test_view_should_not_break_without_tagger(self):
        self.open_content()
        self.selenium.assertTextPresent('Keywords')

    @unittest.skip('foo')
    def test_update_should_load_tags(self):
        tags = self.setup_tags()
        self.open_content()
        s = self.selenium
        tags['t1'] = self.get_tag('t1')
        s.clickAndWait('css=button[href="#update_tags"]')
        s.waitForTextPresent('t1')

    @unittest.skip('foo')
    def test_update_should_honour_disabled_tags(self):
        tags = self.setup_tags()
        self.open_content()
        s = self.selenium
        tags['t1'] = self.get_tag('t1')
        tags['t1'].disabled = True
        s.clickAndWait('css=button[href="#update_tags"]')
        s.waitForElementPresent('id=form.keywords.0')
        s.assertNotChecked('id=form.keywords.0')

    @unittest.skip('foo')
    def test_save_should_work_after_update(self):
        tags = self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.clickAndWait('css=button[href="#update_tags"]')
        s.pause(100)
        s.clickAndWait('name=form.actions.apply')
        s.assertChecked('id=form.keywords.0')
