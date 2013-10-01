import zeit.content.article.edit.browser.testing


class Supertitle(zeit.content.article.edit.browser.testing.EditorTestCase):

    supertitle = 'article-content-head.supertitle'
    teaser_supertitle = 'teaser-supertitle.teaserSupertitle'

    layer = zeit.content.article.testing.WEBDRIVER_LAYER

    def setUp(self):
        super(Supertitle, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=%s' % self.teaser_supertitle)

    def test_teaser_supertitle_is_copied_to_article_supertitle_if_empty(self):
        s = self.selenium
        self.eval('document.getElementById("%s").value = ""' % self.supertitle)
        s.click('//a[@href="edit-form-teaser"]')
        s.type('id=%s' % self.teaser_supertitle, 'super\t')
        s.assertValue('id=%s' % self.supertitle, 'super')
