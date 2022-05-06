from zeit.content.article.interfaces import IArticle
from zope.browser.interfaces import ITerms
import zeit.content.article.testing
import zope.component
import zope.publisher.browser


class TestAdding(zeit.content.article.testing.BrowserTestCase):

    def setUp(self):
        super().setUp()
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/online/2007/01/')

    def get_article(self):
        import zeit.cms.workingcopy.interfaces
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(None)
        return list(wc.values())[0]

    def test_ressort_should_be_set_from_url(self):
        request = zope.publisher.browser.TestRequest()
        terms = zope.component.getMultiAdapter(
            (IArticle['ressort'].source(object()), request), ITerms)
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

    def test_channels_should_be_set_to_ressort(self):
        request = zope.publisher.browser.TestRequest()
        terms = zope.component.getMultiAdapter(
            (IArticle['ressort'].source(object()), request), ITerms)
        ressort_token = terms.getTerm('Deutschland').token
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        url = '{0}?form.ressort={1}'.format(url, ressort_token)
        self.browser.open(url)
        article = self.get_article()
        self.assertEqual((('Deutschland', None),), article.channels)

    def test_genre_should_be_set_from_url(self):
        request = zope.publisher.browser.TestRequest()
        terms = zope.component.getMultiAdapter(
            (IArticle['genre'].source(object()), request), ITerms)
        genre_token = terms.getTerm('nachricht').token
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        url = '{0}?form.genre={1}'.format(url, genre_token)
        self.browser.open(url)
        article = self.get_article()
        self.assertEqual('nachricht', article.genre)

    def test_authorship_should_be_set_from_url(self):
        repo = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        author = zeit.content.author.author.Author()
        author.firstname = 'William'
        author.lastname = 'Shakespeare'
        repo['author'] = author
        principal = (
            zope.security.management.getInteraction().
            participations[0].principal)
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
        clipboard.addClip("me")
        me = clipboard['me']
        entry = zeit.cms.clipboard.interfaces.IClipboardEntry(
            repo['author'])
        me['author'] = entry
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        url = '{0}?form.authorships=me'.format(url)
        self.browser.open(url)
        article = self.get_article()
        self.assertEqual('http://xml.zeit.de/author',
                         article.authorships[0].target.uniqueId)
        url = menu.value[0]
        url = '{0}?form.authorships=you'.format(url)
        self.browser.open(url)
        article = self.get_article()
        self.assertEqual((), article.authorships)
        url = menu.value[0]
        url = '{0}?form.authorships={1}'.format(
            url, 'http%3A%2F%2Fxml.zeit.de%2Fauthor')
        self.browser.open(url)
        article = self.get_article()
        self.assertEqual('http://xml.zeit.de/author',
                         article.authorships[0].target.uniqueId)

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
        self.browser.open('@@edit.form.new-filename?show_form=yes')
        ctrl = self.browser.getControl('New file name')
        self.assertEqual('', ctrl.value)

    def test_filename_should_not_be_editable_when_article_is_not_renameable(
            self):
        self.browser.open('Somalia/@@checkout')
        self.browser.open('@@edit-forms')
        self.assertNotIn('filename', self.browser.contents)

    def test_default_values_from_interface_should_be_set(self):
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        self.browser.open(url)
        article = self.get_article()
        self.assertEqual(True, article.commentsAllowed)
        self.assertEqual(False, article.commentsPremoderate)

    def test_new_article_should_have_last_semantic_change(self):
        from zeit.cms.content.interfaces import ISemanticChange
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Article']
        url = menu.value[0]
        self.browser.open(url)
        article = self.get_article()
        self.assertTrue(ISemanticChange(article).last_semantic_change)


class DefaultView(zeit.content.article.testing.BrowserTestCase):

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
