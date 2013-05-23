# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.article.testing


class TestAdding(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.TestBrowserLayer

    def setUp(self):
        super(TestAdding, self).setUp()
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/online/2007/01/')

    def get_article(self):
        import zeit.cms.workingcopy.interfaces
        with zeit.cms.testing.site(self.getRootFolder()):
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

    def test_article_should_be_renameable(self):
        from zeit.cms.repository.interfaces import IAutomaticallyRenameable
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        self.browser.open(url)
        article = self.get_article()
        self.assertTrue(IAutomaticallyRenameable(article).renameable)
        self.assertFalse(IAutomaticallyRenameable(article).rename_to)

    def test_filename_should_be_editable_when_article_is_renameable(self):
        from zeit.cms.repository.interfaces import IAutomaticallyRenameable
        self.browser.open('Somalia/@@checkout')
        article = self.get_article()
        IAutomaticallyRenameable(article).renameable = True
        self.browser.handleErrors = False
        self.browser.open('@@edit.form.new-filename?show_form=yes')
        ctrl = self.browser.getControl('New file name')
        self.assertEqual('', ctrl.value)

    def test_filename_should_not_be_editable_when_article_is_not_renameable(
            self):
        self.browser.open('Somalia/@@checkout')
        self.get_article()
        self.browser.open('@@edit-forms')
        self.assertNotIn('filename', self.browser.contents)

    def test_default_values_from_interface_should_be_set(self):
        from zeit.content.article.interfaces import ICDSWorkflow
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        self.browser.open(url)
        article = self.get_article()
        self.assertEqual(True, article.dailyNewsletter)
        self.assertEqual(True, ICDSWorkflow(article).export_cds)


class DefaultView(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.TestBrowserLayer

    def test_in_repository_shows_edit_view_readonly(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/Somalia')
        # we can't really check whether it's readonly since the editor comes in
        # via Javascript, so we content ourselves with a smoke check.
        self.assertEllipsis('...<div id="cp-content">...', b.contents)

    def test_in_repository_but_already_checked_out_redirects_to_wc(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/Somalia'
            '/@@checkout')
        b.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/Somalia')
        self.assertIn('workingcopy', b.url)

    def test_in_repository_with_ghost_just_shows_edit_view(self):
        # XXX tests don't load zeit.ghost, so this test doesn't really test
        # anything
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/Somalia'
            '/@@checkout')
        b.open('@@checkin')
        self.assertEllipsis('...<div id="cp-content">...', b.contents)

    def test_in_workingcopy_shows_edit_view(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/online/2007/01/Somalia'
            '/@@checkout')
        self.assertEllipsis('...<div id="cp-content">...', b.contents)
