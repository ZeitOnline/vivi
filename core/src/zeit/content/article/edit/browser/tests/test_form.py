# coding: utf-8
# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.workflow.interfaces import IPublish
from zeit.content.article.article import Article
from zeit.content.article.interfaces import ICDSWorkflow
from zeit.workflow.interfaces import IContentWorkflow
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.article.testing
import zeit.workflow.testing


class MemoTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_memo_is_editable_while_checked_in(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['article'] = Article()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/article/@@edit.form.memo?show_form=1')
        b.getControl('Memo').value = 'foo bar baz'
        b.getControl('Apply').click()
        # reload() forgets the query-paramter, sigh.
        b.open('http://localhost/++skin++vivi/repository'
               '/article/@@edit.form.memo?show_form=1')
        self.assertEqual('foo bar baz', b.getControl('Memo').value)


class ReadonlyTest(zeit.cms.testing.BrowserTestCase):
    """Sample test to make sure the view of a checked-in article displays
    widgets in read-only mode.

    """

    layer = zeit.content.article.testing.TestBrowserLayer

    def setUp(self):
        super(ReadonlyTest, self).setUp()
        self.browser.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/Somalia'
            '/@@edit-forms')

    def test_text_is_displayed(self):
        self.assertEllipsis(
            '...<div class="widget display">2007</div>...',
            self.browser.contents)

    def test_text_is_not_editable(self):
        with self.assertRaises(LookupError):
            self.browser.getControl('Year')


class WorkflowStatusDisplayTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_displays_status_fields_as_checkboxes(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                somalia = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')
                IContentWorkflow(somalia).corrected = True

        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/online/2007/01/Somalia/@@checkout')
        b.open('@@edit.form.workflow-display?show_form=1')
        self.assertFalse(b.getControl('Edited').selected)
        self.assertTrue(b.getControl('Corrected').selected)

    def test_displays_last_published_information(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                article = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')
                IContentWorkflow(article).urgent = True
                # silence annoying error message
                ICDSWorkflow(article).export_cds = False
                IPublish(article).publish()
                zeit.workflow.testing.run_publish()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/online/2007/01/Somalia/@@checkout')
        b.open('@@contents')
        self.assertEllipsis(
            '...zuletzt veröffentlicht am...von...zope.user...', b.contents)


class PageNumberDisplay(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def test_no_page_displays_as_not_applicable(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/online/2007/01/Somalia/@@checkout')
        b.open('@@edit.form.options-b')
        self.assertEllipsis('...Page...n/a...', b.contents)

    def test_existing_page_number_is_displayed(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                article = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia')
                with zeit.cms.checkout.helper.checked_out(article) as co:
                    co.page = '4711'
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/online/2007/01/Somalia/@@checkout')
        b.open('@@edit.form.options-b')
        self.assertEllipsis('...Page...4711...', b.contents)


class HeaderSync(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(HeaderSync, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=options-b.year')

    def test_header_is_reloaded_after_change_to_ressort(self):
        s = self.selenium
        s.assertSelectedLabel('id=metadata-a.ressort', 'International')
        s.assertText('id=editor-forms-heading', '*International*')
        s.select('id=metadata-a.ressort', 'Deutschland')
        s.fireEvent('id=metadata-a.ressort', 'blur')
        s.waitForElementNotPresent('css=.field.dirty')
        s.assertText('id=editor-forms-heading', '*Deutschland*')

    # XXX there are several more inline forms that trigger a reload of the
    # header. Should we write tests for all of them?


class CharLimit(zeit.content.article.edit.browser.testing.EditorTestCase):

    def setUp(self):
        super(CharLimit, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')

    def test_teaser_supertitle_has_character_limit(self):
        s = self.selenium
        s.waitForElementPresent('css=.fieldname-teaserSupertitle')
        s.assertElementPresent('css=.fieldname-teaserSupertitle .charlimit')

    def test_teaser_title_has_character_limit(self):
        s = self.selenium
        s.waitForElementPresent('css=.fieldname-teaserTitle')
        s.assertElementPresent('css=.fieldname-teaserTitle .charlimit')

    def test_teaser_text_has_character_limit(self):
        s = self.selenium
        s.waitForElementPresent('css=.fieldname-teaserText')
        s.assertElementPresent('css=.fieldname-teaserText .charlimit')
