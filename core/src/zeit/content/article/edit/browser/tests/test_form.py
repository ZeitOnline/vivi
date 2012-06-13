# coding: utf-8
# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.workflow.interfaces import IPublish
from zeit.content.article.article import Article
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
               '/article/@@edit.form.memo-diver?show_form=1')
        b.getControl('Memo').value = 'foo bar baz'
        b.getControl('Apply').click()
        # reload() forgets the query-paramter, sigh.
        b.open('http://localhost/++skin++vivi/repository'
               '/article/@@edit.form.memo-diver?show_form=1')
        self.assertEqual('foo bar baz', b.getControl('Memo').value)


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
                IPublish(article).publish()
                zeit.workflow.testing.run_publish()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/online/2007/01/Somalia/@@checkout')
        b.open('@@contents')
        self.assertEllipsis(
            '...zuletzt veröffentlicht am...von...zope.user...', b.contents)
