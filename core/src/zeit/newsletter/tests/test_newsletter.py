# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree
import mock
import unittest2 as unittest
import zeit.cms.testing
import zeit.newsletter.testing
import zope.component


class NewsletterObjectsTest(zeit.newsletter.testing.TestCase,
                            zeit.cms.testing.BrowserAssertions):

    def test_block_factories_are_wired_up_correctly(self):
        from zeit.newsletter.newsletter import Newsletter, Group, Teaser
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

        xml = lxml.etree.tostring(newsletter.xml, pretty_print=True)
        self.assert_ellipsis("""\
<newsletter...>
  <head/>
  <body>
    <region cp:type="group"...>
      <container cp:type="teaser"...>
    </region>
  </body>
</newsletter>
""", xml)

    def test_newsletter_should_be_addable_to_repository(self):
        from zeit.newsletter.newsletter import Newsletter
        self.repository['newsletter'] = Newsletter()
        newsletter = self.repository['newsletter']
        self.assertIsInstance(newsletter, Newsletter)


class NewsletterInterfaceTest(unittest.TestCase):

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
        from zeit.newsletter.newsletter import Newsletter
        import zeit.cms.repository.folder
        super(SendTest, self).setUp()
        self.repository['mynl'] = zeit.cms.repository.folder.Folder()
        self.repository['mynl']['newsletter'] = Newsletter()
        self.newsletter = self.repository['mynl']['newsletter']
        self.newsletter.subject = 'thesubject'

    def test_send_uses_renderer_and_calls_optivo(self):
        with mock.patch('zeit.newsletter.interfaces.IRenderer') as renderer:
            with mock.patch('zope.component.getUtility') as getUtility:
                renderer().html = mock.sentinel.html
                renderer().text = mock.sentinel.text
                self.newsletter.send()
                optivo = getUtility()
                optivo.send.assert_called_with(
                    'mynl', 'thesubject',
                    mock.sentinel.html, mock.sentinel.text)

    def test_send_test_passes_recipient_to_optivo(self):
        with mock.patch('zeit.newsletter.interfaces.IRenderer') as renderer:
            with mock.patch('zope.component.getUtility') as getUtility:
                renderer().html = mock.sentinel.html
                renderer().text = mock.sentinel.text
                self.newsletter.send_test('test@example.com')
                optivo = getUtility()
                optivo.test.assert_called_with(
                    'mynl', 'test@example.com', 'thesubject',
                    mock.sentinel.html, mock.sentinel.text)
