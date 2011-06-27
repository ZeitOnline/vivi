# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.newsletter.testing
import zope.component


class NewsletterObjectsTest(zeit.newsletter.testing.TestCase):

    def test_block_factories_are_wired_up_correctly(self):
        from zeit.newsletter.newsletter import Newsletter, Group, Teaser
        newsletter = Newsletter()
        body = newsletter['body']
        self.assertEqual([], body.keys())

        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, name='group')
        group = factory()
        self.assertTrue(isinstance(group, Group))
        self.assertEqual([], group.keys())
        self.assertEqual([group.__name__], body.keys())

        factory = zope.component.getAdapter(
            group, zeit.edit.interfaces.IElementFactory, name='teaser')
        teaser = factory()
        self.assertTrue(isinstance(teaser, Teaser))
