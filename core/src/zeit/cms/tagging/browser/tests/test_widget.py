# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.cms.testing


class TestWidget(zeit.cms.testing.SeleniumTestCase):

    def get_tag(self, code):
        tag = mock.Mock()
        tag.code = tag.label = code
        tag.disabled = False
        return tag

    def setup_tags(self, *codes):
        import stabledict
        class Tags(stabledict.StableDict):
            pass
        tags = Tags()
        for code in codes:
            tags[code] = self.get_tag(code)
        patcher = mock.patch('zeit.cms.tagging.interfaces.ITagger')
        self.addCleanup(patcher.stop)
        self.tagger = patcher.start()
        self.tagger.return_value = tags
        tags.updateOrder = mock.Mock()
        tags.update = mock.Mock()
        return tags

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
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.dragAndDropToObject(
            "xpath=//li[contains(., 't1')]",
            "xpath=//li[contains(., 't3')]")
        s.assertTextPresent('t2*t3*t1*t4')
        s.clickAndWait('name=form.actions.apply')
        self.assertEqual(
            ['t2', 't3', 't1', 't4'],
            list(self.tagger().updateOrder.call_args[0][0]))

    def test_unchecked_tags_should_be_disabled(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.click("xpath=//li/label[contains(., 't1')]")
        s.clickAndWait('name=form.actions.apply')
        self.assertNotIn('t1', self.tagger())
        self.assertIn('t2', self.tagger())

    def test_view_should_not_break_without_tagger(self):
        self.open_content()
        self.selenium.assertTextPresent('Keywords')

    def test_update_should_load_tags(self):
        tags = self.setup_tags()
        self.open_content()
        s = self.selenium
        tags['t1'] = self.get_tag('t1')
        s.click('css=a[href="#update_tags"]')
        s.waitForTextPresent('t1')
        self.assertTrue(self.tagger().update.called)

    def test_save_should_work_after_update(self):
        self.setup_tags('t1', 't2', 't3', 't4')
        self.open_content()
        s = self.selenium
        s.click('css=a[href="#update_tags"]')
        s.pause(100)
        s.clickAndWait('name=form.actions.apply')
        s.assertChecked('id=form.keywords.0')
