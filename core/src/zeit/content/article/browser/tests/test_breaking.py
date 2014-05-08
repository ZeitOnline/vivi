from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublishInfo
import zeit.cms.testing
import zeit.content.article.testing


class TestAdding(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.TestBrowserLayer

    def setUp(self):
        super(TestAdding, self).setUp()
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/online/2007/01/')

    def test_default_values_should_be_set(self):
        b = self.browser
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Breaking news']
        b.open(menu.value[0])
        b.getControl('Ressort').displayValue = ['International']
        b.getControl('Title').value = 'Mytitle'
        b.getControl('File name').value = 'foo'
        b.getControl('Publish and push').click()

        with zeit.cms.testing.site(self.getRootFolder()):
            article = ICMSContent('http://xml.zeit.de/online/2007/01/foo')
            # XXX Kind of duplicate from .test_form.TestAdding
            self.assertEqual(2008, article.year)
            self.assertEqual(26, article.volume)
            self.assertEqual('ZEDE', article.product.id)
            self.assertEqual(True, article.commentsAllowed)

            # XXX Split into separate test?
            self.assertEqual(True, IPublishInfo(article).urgent)
