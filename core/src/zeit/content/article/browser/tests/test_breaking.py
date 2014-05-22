from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.edit.interfaces import IEditableBody
import zeit.cms.testing
import zeit.content.article.interfaces
import zeit.content.article.testing
import zope.i18n.translationdomain


class TestAdding(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.article.testing.TestBrowserLayer

    def setUp(self):
        super(TestAdding, self).setUp()
        domain = zope.i18n.translationdomain.TranslationDomain('zeit.cms')
        self.zca.patch_utility(domain, name='zeit.cms')
        self.catalog = zeit.cms.testing.TestCatalog()
        domain.addCatalog(self.catalog)

        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/online/2007/01/')

    def create_breakingnews(self):
        b = self.browser
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Add breaking news']
        b.open(menu.value[0])

    def fill_in_required_values(self):
        b = self.browser
        b.getControl('Ressort').displayValue = ['International']
        b.getControl('Title').value = 'Mytitle'
        b.getControl('File name').value = 'foo'

    def test_default_values_should_be_set(self):
        self.create_breakingnews()
        self.fill_in_required_values()
        self.browser.getControl('Publish and push').click()

        with zeit.cms.testing.site(self.getRootFolder()):
            article = ICMSContent('http://xml.zeit.de/online/2007/01/foo')
            # XXX Kind of duplicate from .test_form.TestAdding
            self.assertEqual(2008, article.year)
            self.assertEqual(26, article.volume)
            self.assertEqual('ZEDE', article.product.id)
            self.assertEqual(True, article.commentsAllowed)

            # XXX Split into separate test?
            self.assertEqual(True, IPublishInfo(article).urgent)
            push = zeit.push.interfaces.IPushMessages(article)
            self.assertEqual(True, push.enabled)
            self.assertIn({'type': 'homepage'}, push.message_config)
            self.assertIn({'type': 'parse', 'title': 'Eilmeldung'},
                          push.message_config)
            self.assertEqual(article.title, push.short_text)

    def test_setting_body_text_creates_paragraph(self):
        self.create_breakingnews()
        self.fill_in_required_values()
        self.browser.getControl('Article body').value = 'mytext'
        self.browser.getControl('Publish and push').click()

        with zeit.cms.testing.site(self.getRootFolder()):
            article = ICMSContent('http://xml.zeit.de/online/2007/01/foo')
            body = IEditableBody(article)
            para = body.values()[1]  # 0 is image
            self.assertEqual('mytext', para.text)

    def test_body_text_not_given_creates_no_paragraph(self):
        self.create_breakingnews()
        self.fill_in_required_values()
        self.browser.getControl('Article body').value = ''
        self.browser.getControl('Publish and push').click()

        with zeit.cms.testing.site(self.getRootFolder()):
            article = ICMSContent('http://xml.zeit.de/online/2007/01/foo')
            body = IEditableBody(article)
            self.assertEqual(1, len(body))

    def test_body_text_default_value_is_translated(self):
        b = self.browser
        b.addHeader('Accept-Language', 'tt')
        self.catalog.messages['breaking-news-more-shortly'] = 'foo'
        self.create_breakingnews()
        self.assertEqual('foo', b.getControl('Article body').value)

    def test_title_has_max_length(self):
        # ICommonMetadata.title only has a charlimit annotation=75, but no max
        # length (due to Print articles, IIRC), but for breaking news we want
        # a hard limit of 30 due to the mobile devices.
        self.create_breakingnews()
        self.fill_in_required_values()
        b = self.browser
        b.getControl('Title').value = 'a' * (
            zeit.content.article.interfaces.IBreakingNews[
                'title'].max_length + 1)
        b.getControl('Publish and push').click()
        self.assertEllipsis('...too long...', b.contents)
