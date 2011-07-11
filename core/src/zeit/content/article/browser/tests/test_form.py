# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest2
import zeit.cms.testing
import zeit.cms.testing
import zeit.content.article.testing


class TestAdding(unittest2.TestCase,
                 zeit.cms.testing.BrowserAssertions):

    layer = zeit.content.article.testing.TestBrowserLayer

    def setUp(self):
        from zope.testbrowser.testing import Browser
        self.browser = browser = Browser()
        browser.addHeader('Authorization', 'Basic user:userpw')
        browser.open('http://localhost:8080/++skin++vivi/repository/online'
                     '/2007/01/')

    def get_article(self):
        import zeit.cms.workingcopy.interfaces
        with zeit.cms.testing.site(self.layer.setup.getRootFolder()):
            with zeit.cms.testing.interaction():
                wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(None)
                return list(wc.values())[0]

    def test_ressort_should_be_set_from_url(self):
        from zeit.content.article.interfaces import IArticle
        from zope.browser.interfaces import ITerms
        import zope.component
        import zope.publisher.browser
        request = zope.publisher.browser.TestRequest()
        terms = zope.component.getMultiAdapter(
            (IArticle['ressort'].source, request), ITerms)
        ressort_token = terms.getTerm('Deutschland').token
        terms = zope.component.getMultiAdapter(
            (IArticle['sub_ressort'].source(object()), request), ITerms)
        sub_ressort_token = terms.getTerm('Integration').token
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        url = '{0}?form.ressort={1}&form.sub_ressort={2}'.format(
            url, ressort_token, sub_ressort_token)
        self.browser.open(url)
        article = self.get_article()
        self.assertEqual('Deutschland', article.ressort)
        self.assertEqual('Integration', article.sub_ressort)

    def test_default_year_and_volume_should_be_set(self):
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        self.browser.open(url)
        article = self.get_article()
        self.assertEqual(2008, article.year)
        self.assertEqual(26, article.volume)

    def test_default_product_should_be_set(self):
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        self.browser.handleErrors = False
        self.browser.open(url)
        article = self.get_article()
        self.assertEqual('ZEDE', article.product.id)

    def test_article_should_be_renamable(self):
        from zeit.cms.repository.interfaces import IAutomaticallyRenameable
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        self.browser.open(url)
        article = self.get_article()
        self.assertTrue(IAutomaticallyRenameable(article).renamable)
        self.assertFalse(IAutomaticallyRenameable(article).rename_to)

    def test_filename_should_be_editable_when_article_is_renamable(self):
        from zeit.cms.repository.interfaces import IAutomaticallyRenameable
        self.browser.open('Somalia/@@checkout')
        article = self.get_article()
        IAutomaticallyRenameable(article).renamable = True
        self.browser.handleErrors = False
        self.browser.open('@@edit.form.metadata-c?show_form=yes')
        ctrl = self.browser.getControl('New file name')
        self.assertEqual('', ctrl.value)

    def test_filename_should_not_be_editable_when_article_is_not_renamable(
            self):
        self.browser.open('Somalia/@@checkout')
        article = self.get_article()
        self.browser.open('@@edit.form.metadata-c?show_form=yes')
        with self.assertRaises(LookupError):
            self.browser.getControl('New file name')
        self.assert_ellipsis('...<div class="widget">Somalia</div>...')
