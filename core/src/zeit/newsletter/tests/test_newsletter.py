from datetime import datetime
from unittest import mock
from zeit.cms.checkout.helper import checked_out
import pytz
import zeit.cms.testing
import zeit.newsletter.testing
import zeit.optivo.interfaces
import zope.component


class NewsletterObjectsTest(zeit.newsletter.testing.TestCase,
                            zeit.cms.testing.BrowserAssertions):

    def test_block_factories_are_wired_up_correctly(self):
        from zeit.newsletter.newsletter import (
            Newsletter, Group, Teaser,
            MiddleAdvertisement, ThisWeeksAdvertisement, BottomAdvertisement
        )
        newsletter = Newsletter()
        body = newsletter['newsletter_body']
        self.assertEqual([], body.keys())

        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, name='group')
        group = factory()
        self.assertIsInstance(group, Group)
        self.assertEqual([], group.keys())
        self.assertEqual([group.__name__], body.keys())

        factory = zope.component.getAdapter(
            group, zeit.edit.interfaces.IElementFactory, name='teaser')
        teaser = factory()
        self.assertIsInstance(teaser, Teaser)

        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory,
            name='advertisement-middle')
        advertisement = factory()
        self.assertIsInstance(advertisement, MiddleAdvertisement)

        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory,
            name='advertisement-thisweeks')
        advertisement = factory()
        self.assertIsInstance(advertisement, ThisWeeksAdvertisement)

        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory,
            name='advertisement-bottom')
        advertisement = factory()
        self.assertIsInstance(advertisement, BottomAdvertisement)

        xml = zeit.cms.testing.xmltotext(newsletter.xml)
        self.assert_ellipsis("""\
<newsletter...>
  <head/>
  <body>
    <region cp:type="group"...>
      <container cp:type="teaser"...>
    </region>
    <container cp:type="advertisement-middle".../>
    <container cp:type="advertisement-thisweeks".../>
    <container cp:type="advertisement-bottom".../>
  </body>
</newsletter>
""", xml)

    def test_newsletter_should_be_addable_to_repository(self):
        from zeit.newsletter.newsletter import Newsletter
        self.repository['newsletter'] = Newsletter()
        newsletter = self.repository['newsletter']
        self.assertIsInstance(newsletter, Newsletter)

    def test_finds_category_by_walking_up_parents(self):
        from zeit.newsletter.category import NewsletterCategory
        from zeit.newsletter.interfaces import INewsletterCategory
        from zeit.newsletter.newsletter import Newsletter
        nl = self.repository['foo'] = Newsletter()
        self.assertEqual(None, INewsletterCategory(nl, None))
        self.repository['newsletter'] = zeit.cms.repository.folder.Folder()
        self.repository['newsletter']['taeglich'] = NewsletterCategory()
        nl = self.repository['newsletter']['taeglich']['one'] = Newsletter()
        self.assertEqual(
            self.repository['newsletter']['taeglich'], INewsletterCategory(nl))


class NewsletterInterfaceTest(zeit.newsletter.testing.TestCase):

    def get_newsletter(self):
        from zeit.newsletter.newsletter import Newsletter
        return Newsletter()

    def test_should_pass_verification(self):
        from zeit.newsletter.interfaces import INewsletter
        import zope.interface.verify
        zope.interface.verify.verifyObject(INewsletter, self.get_newsletter())

    def test_keys_should_return_body(self):
        self.assertEqual(['newsletter_body'], self.get_newsletter().keys())


class SendTest(zeit.newsletter.testing.TestCase):

    def setUp(self):
        from zeit.newsletter.category import NewsletterCategory
        from zeit.newsletter.newsletter import Newsletter
        import zeit.cms.repository.folder
        super().setUp()
        category = NewsletterCategory()
        category.mandant = '12345'
        category.recipientlist = 'recipientlist'
        category.recipientlist_test = 'recipientlist_test'
        self.repository['mynl'] = category
        self.repository['mynl']['newsletter'] = Newsletter()
        self.newsletter = self.repository['mynl']['newsletter']
        self.newsletter.subject = 'thesubject'

        self.renderer = mock.Mock()
        zope.component.getGlobalSiteManager().registerUtility(
            self.renderer, zeit.newsletter.interfaces.IRenderer)
        self.renderer.return_value = dict(
            html=mock.sentinel.html, text=mock.sentinel.text)

        self.optivo = zope.component.getUtility(zeit.optivo.interfaces.IOptivo)
        self.optivo.reset()

    def test_send_uses_renderer_and_calls_optivo(self):
        self.newsletter.send()
        self.assertEqual(
            ('send', 12345, 'recipientlist', 'thesubject',
             mock.sentinel.html, mock.sentinel.text), self.optivo.calls[0])

    def test_send_test_passes_recipient_to_optivo(self):
        self.newsletter.send_test('test@example.com')
        self.assertEqual(
            ('test', 12345, 'recipientlist_test',
             'test@example.com', '[test] thesubject',
             mock.sentinel.html, mock.sentinel.text), self.optivo.calls[0])

    def test_send_updates_timestamp_even_when_error(self):
        with checked_out(self.newsletter) as co:
            zope.dublincore.interfaces.IDCTimes(co).created = datetime.now(
                pytz.UTC)
        self.renderer.side_effect = RuntimeError('provoked')
        category = self.repository['mynl']
        self.assertEqual(None, category.last_created)
        with self.assertRaises(RuntimeError):
            self.newsletter.send()
        self.assertNotEqual(None, category.last_created)
