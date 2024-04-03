from unittest import mock

import lxml.etree
import transaction
import zope.i18n.translationdomain

from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
import zeit.cms.checkout.helper
import zeit.content.article.interfaces
import zeit.content.article.testing


class TestAdding(zeit.content.article.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        domain = zope.i18n.translationdomain.TranslationDomain('zeit.cms')
        zope.component.getGlobalSiteManager().registerUtility(domain, name='zeit.cms')
        self.catalog = zeit.cms.testing.TestCatalog()
        domain.addCatalog(self.catalog)

        for _name, notifier in zope.component.getUtilitiesFor(zeit.push.interfaces.IPushNotifier):
            notifier.reset()

        self.browser.open('http://localhost:8080/++skin++vivi/repository/online/2007/01/')

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
        article = ICMSContent('http://xml.zeit.de/online/2007/01/foo')
        # XXX Kind of duplicate from .test_form.TestAdding
        self.assertEqual(2008, article.year)
        self.assertEqual(26, article.volume)
        self.assertEqual('ZEDE', article.product.id)
        self.assertEqual(True, article.commentsAllowed)
        self.assertEqual(False, article.commentsPremoderate)

    def test_marks_article_as_breaking(self):
        self.create_breakingnews()
        self.fill_in_required_values()
        self.browser.getControl('Publish and push').click()
        article = ICMSContent('http://xml.zeit.de/online/2007/01/foo')
        self.assertEqual(True, zeit.content.article.interfaces.IBreakingNews(article).is_breaking)
        self.assertEllipsis(
            '...<attribute...name="is_breaking">yes</attribute>...',
            zeit.cms.testing.xmltotext(article.xml),
        )

    def test_publish_sends_push_messages(self):
        # This tests the integration with zeit.push, but not the actual push
        # methods themselves.
        self.create_breakingnews()
        self.fill_in_required_values()
        self.browser.getControl('Publish and push').click()
        self.browser.open('@@publish')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/foo')
        self.assertEqual(True, IPublishInfo(article).published)
        for service in ['homepage', 'urbanairship', 'facebook']:
            notifier = zope.component.getUtility(zeit.push.interfaces.IPushNotifier, name=service)
            self.assertEqual(1, len(notifier.calls))
            self.assertEqual(article.title, notifier.calls[0][0])

        urbanairship = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='urbanairship'
        )
        self.assertEqual(
            'eilmeldung.json', urbanairship.calls[0][2]['message'].config['payload_template']
        )
        facebook = zope.component.getUtility(zeit.push.interfaces.IPushNotifier, name='facebook')
        self.assertEqual(
            zeit.push.facebook.facebookAccountSource(None).MAIN_ACCOUNT,
            facebook.calls[0][2]['account'],
        )

    def test_banners_and_mobile_are_disabled_after_publish(self):
        # The breaking news is a normal article, so it has the normal social
        # media functionality, thus it may be "armed" again later on
        # (IPushMessages.enabled). But that should of course only apply to
        # those push services actually meant by the social media UI (i.e.
        # Facebook), and not send "breaking news" messages again
        # (e.g. to mobile devices).
        self.create_breakingnews()
        self.fill_in_required_values()
        self.browser.getControl('Publish and push').click()
        self.browser.open('@@publish')
        article = ICMSContent('http://xml.zeit.de/online/2007/01/foo')
        push = zeit.push.interfaces.IPushMessages(article)
        self.assertIn(
            {
                'type': 'mobile',
                'enabled': False,
                'title': 'Default title',
                'variant': 'manual',
                'payload_template': 'eilmeldung.json',
            },
            push.message_config,
        )
        self.assertIn({'type': 'homepage', 'enabled': False}, push.message_config)

    def test_setting_body_text_creates_paragraph(self):
        self.create_breakingnews()
        self.fill_in_required_values()
        self.browser.getControl('Article body').value = 'mytext'
        self.browser.getControl('Publish and push').click()
        article = ICMSContent('http://xml.zeit.de/online/2007/01/foo')
        para = article.body.values()[1]  # 0 is image
        self.assertEqual('mytext', para.text)

    def test_body_text_not_given_creates_no_paragraph(self):
        self.create_breakingnews()
        self.fill_in_required_values()
        self.browser.getControl('Article body').value = ''
        self.browser.getControl('Publish and push').click()
        article = ICMSContent('http://xml.zeit.de/online/2007/01/foo')
        self.assertEqual(1, len(article.body))

    def test_body_text_default_value_is_translated(self):
        b = self.browser
        b.addHeader('Accept-Language', 'tt')
        self.catalog.messages['breaking-news-more-shortly'] = 'foo'
        self.create_breakingnews()
        self.assertEqual('foo', b.getControl('Article body').value)

    def test_channel_is_populated_from_ressort(self):
        # zeit.addcentral is not loaded, and also mostly JS-driven, so we use
        # model code for setup instead of the browser.
        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSSkin,
            # XXX Why do we have to duplicate the skin information?
            environ={'SERVER_URL': 'http://localhost/++skin++vivi'},
        )
        adder = zeit.cms.content.add.ContentAdder(
            request,
            type_=zeit.content.article.interfaces.IBreakingNews,
            ressort='Deutschland',
            sub_ressort='Meinung',
            year='2018',
            month='01',
        )
        b = self.browser
        b.open(adder())
        self.assertEqual(['Deutschland'], b.getControl('Channel').displayValue)
        self.assertEqual(['Meinung'], b.getControl('Subchannel').displayValue)
        b.getControl('Title').value = 'Mytitle'
        b.getControl('File name').value = 'foo'
        self.browser.getControl('Publish and push').click()
        article = ICMSContent('http://xml.zeit.de/deutschland/meinung/2018-01/foo')
        self.assertEqual((('Deutschland', 'Meinung'),), article.channels)


class RetractBannerTest(zeit.content.article.testing.SeleniumTestCase):
    def setUp(self):
        # We cannot retrieve the state of eager results, so fake them here, as
        # publishing itself is tested elsewhere.
        mocker = mock.patch(
            'celery.result.AsyncResult.state',
            new_callable=mock.PropertyMock,
            return_value='SUCCESS',
        )
        mocker.start()
        self.addCleanup(mocker.stop)
        super().setUp()
        banner_config = zeit.content.rawxml.rawxml.RawXML()
        banner_config.xml = lxml.etree.fromstring(
            '<xml><article_id>' 'http://xml.zeit.de/online/2007/01/Somalia' '</article_id></xml>'
        )
        self.repository['banner'] = banner_config
        IPublish(self.repository['banner']).publish(background=False)

        # Make Somalia breaking news, so the retract section is shown.
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        with zeit.cms.checkout.helper.checked_out(article) as co:
            zeit.content.article.interfaces.IBreakingNews(co).is_breaking = True

        transaction.commit()

    def test_retract_banner_endtoend(self):
        self.open('/repository/online/2007/01/Somalia')
        s = self.selenium
        s.waitForElementPresent('id=breaking-retract')
        s.assertElementPresent('css=#breaking-retract .publish-state.published')
        s.click('id=breaking-retract-banner')
        s.waitForElementPresent('css=.lightbox')
        # Retract happens...
        s.waitForElementNotPresent('css=.lightbox')
        # Button is gone now, since there's nothing to retract anymore
        s.waitForElementNotPresent('id=breaking-retract-banner')
        s.assertNotElementPresent('css=#breaking-retract .publish-state')
