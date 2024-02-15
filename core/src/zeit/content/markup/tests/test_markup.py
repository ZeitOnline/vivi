import string

import zope.event
import zope.lifecycleevent

from zeit.cms.checkout.helper import checked_out
from zeit.cms.testing import xmltotext
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
            co.authorships = [co.authorships.create(self.repository['author'])]
            co.title = 'bah'
            co.text = '<h1>baz</h1>'

        self.assertEqual('bah', self.repository['markup'].title)
        self.assertEqual('Ursula', self.repository['markup'].authorships[0].target.firstname)
        self.assertEqual('<h1>baz</h1>', self.repository['markup'].text.strip())
        self.assertEllipsis('...<h1>baz</h1>...', xmltotext(self.repository['markup'].xml))

    def test_teaser_text_shows_a_shorter_version_of_text(self):
        markup = zeit.content.markup.markup.Markup()
        self.repository['markup'] = markup
        with checked_out(self.repository['markup']) as co:
            co.text = ' '.join(string.ascii_lowercase)

        self.assertEqual('a b c d e f g h i j ...', self.repository['markup'].teaserText)

    def test_teaser_text_shows_nothing_if_text_is_missing(self):
        markup = zeit.content.markup.markup.Markup()
        self.repository['markup'] = markup
        self.assertEqual(None, self.repository['markup'].teaserText)

    def test_teaser_text_only_shortened_if_long_enough(self):
        markup = zeit.content.markup.markup.Markup()
        self.repository['markup'] = markup
        with checked_out(self.repository['markup']) as co:
            co.text = 'a b'

        self.assertEqual('a b', self.repository['markup'].teaserText)
