# Copyright (c) 2011-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2 as unittest


class ModifiedHandlerTest(unittest.TestCase):

    def test_author_references_should_be_copied_to_freetext(self):
        from zope.lifecycleevent import ObjectModifiedEvent, Attributes
        from zeit.cms.content.interfaces import ICommonMetadata
        from zeit.content.author.author import update_author_freetext
        content = mock.Mock()
        author1, author2 = mock.Mock(), mock.Mock()
        author1.display_name = mock.sentinel.author1
        author2.display_name = mock.sentinel.author2
        content.author_references = (author1, author2)
        event = ObjectModifiedEvent(content, Attributes(ICommonMetadata,
                                                        'author_references'))
        update_author_freetext(content, event)
        self.assertEqual([mock.sentinel.author1, mock.sentinel.author2],
                         content.authors)

    def test_author_references_should_not_be_copied_for_other_field_change(
        self):
        from zope.lifecycleevent import ObjectModifiedEvent, Attributes
        from zeit.cms.content.interfaces import ICommonMetadata
        from zeit.content.author.author import update_author_freetext
        content = mock.Mock()
        content.authors = mock.sentinel.unchanged
        author1, author2 = mock.Mock(), mock.Mock()
        content.author_references = (author1, author2)
        event = ObjectModifiedEvent(content, Attributes(ICommonMetadata,
                                                        'some-field'))
        update_author_freetext(content, event)
        self.assertEqual(mock.sentinel.unchanged, content.authors)

    def test_author_references_should_clear_authors_when_empty(self):
        from zope.lifecycleevent import ObjectModifiedEvent, Attributes
        from zeit.cms.content.interfaces import ICommonMetadata
        from zeit.content.author.author import update_author_freetext
        content = mock.Mock()
        content.authors = mock.sentinel.unchanged
        content.author_references = ()
        event = ObjectModifiedEvent(content, Attributes(ICommonMetadata,
                                                        'author_references'))
        update_author_freetext(content, event)
        self.assertEqual([], content.authors)
