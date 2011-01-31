# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest


class TestTagsForContent(unittest.TestCase):

    def get_source(self):
        from zeit.cms.tagging.interfaces import TagsForContent
        return TagsForContent().factory

    def test_get_values_should_be_empty_without_tagger(self):
        self.assertEqual([], self.get_source().getValues(None))

    def test_get_values_should_call_getitem_for_each_element(self):
        source = self.get_source()
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger.return_value = dict(
                foo=mock.sentinel.foo,
                bar=mock.sentinel.bar)
            result = set(source.getValues(mock.sentinel.context))
        self.assertEqual(
            set([mock.sentinel.foo, mock.sentinel.bar]),
            result)

    def test_get_values_should_adapt_context_to_ITagger(self):
        source = self.get_source()
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger.return_value = None
            source.getValues(mock.sentinel.context)
        tagger.asser_called_with(mock.sentinel.context)

    def test_get_title_returns_label(self):
        tag = mock.Mock()
        tag.label = mock.sentinel.label
        self.assertEqual(
            mock.sentinel.label,
            self.get_source().getTitle(mock.sentinel.context, tag))
