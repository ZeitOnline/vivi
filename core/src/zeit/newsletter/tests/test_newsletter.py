# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest2 as unittest
import zeit.newsletter.testing
import zope.component


class NewsletterObjectsTest(zeit.newsletter.testing.TestCase):

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
