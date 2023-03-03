from zeit.cms.checkout.helper import checked_out
from zeit.cms.testing import xmltotext

import zope.event
import zope.lifecycleevent

import zeit.content.author.author
import zeit.content.markup.markup
import zeit.content.markup.testing


class MarkupTest(zeit.content.markup.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        author = zeit.content.author.author.Author()
        author.firstname = 'Ursula'
        author.lastname = 'Marvin'
        self.repository['author'] = author
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(author))

    def test_add_markup_module(self):
        markup = zeit.content.markup.markup.Markup()
        self.repository['markup'] = markup
        with checked_out(self.repository['markup']) as co:
            co.authorships = [co.authorships.create(
                self.repository['author'])]
            co.title = 'bah'
            co.text = '<h1>baz</h1>'

        self.assertEqual('bah', self.repository['markup'].title)
        self.assertEqual(
            'Ursula',
            self.repository['markup'].authorships[0].target.firstname)
        self.assertEqual('<h1>baz</h1>', self.repository['markup'].text)
        self.assertEllipsis(
            '...<h1>baz</h1>...', xmltotext(self.repository['markup'].xml))
