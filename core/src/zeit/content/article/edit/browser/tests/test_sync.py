import unittest2 as unittest
import zeit.content.article.edit.browser.testing


class Supertitle(zeit.content.article.edit.browser.testing.EditorTestCase):

    st = 'article-content-head.supertitle'
    tst = 'teaser-supertitle.teaserSupertitle'

    def setUp(self):
        super(Supertitle, self).setUp()
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        self.selenium.waitForElementPresent('id=%s' % self.tst)

    @unittest.skip('type() does not work, not even the work-around does')
    def test_teaser_supertitle_is_synchronised_to_article_supertitle(self):
        s = self.selenium
        # XXX type() doesn't work with selenium-1 and FF>7
        self.eval('document.getElementById("%s").value = "super"' % self.tst)
        s.fireEvent('id=%s' % self.tst, 'changed')
        s.waitForElementPresent(
            '//input[@id="%s" and @value="super"]' % self.st)
