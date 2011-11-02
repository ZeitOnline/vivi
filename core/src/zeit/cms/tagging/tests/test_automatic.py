# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest


class AutomaticTagSourceTest(unittest.TestCase):

    def get_source(self, context=mock.sentinel.context):
        from zeit.cms.tagging.automatic import AutomaticTagSource
        return AutomaticTagSource(context).factory

    def test_get_values_should_be_empty_without_tagger(self):
        NOT_CONTENT = None
        self.assertEqual([], self.get_source(NOT_CONTENT).getValues())

    def test_get_values_should_call_getitem_for_each_element(self):
        source = self.get_source()
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger.return_value = dict(
                foo=mock.sentinel.foo,
                bar=mock.sentinel.bar)
            result = set(source.getValues())
        self.assertEqual(
            set([mock.sentinel.foo, mock.sentinel.bar]),
            result)

    def test_get_values_should_adapt_context_to_ITagger(self):
        source = self.get_source()
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger.return_value = None
            source.getValues()
        tagger.asser_called_with(mock.sentinel.context)

    def test_get_title_returns_label(self):
        tag = mock.Mock()
        tag.label = mock.sentinel.label
        self.assertEqual(
            mock.sentinel.label,
            self.get_source().getTitle(tag))

    def test_get_token_should_return_code(self):
        tag = mock.Mock()
        tag.code = mock.sentinel.code
        self.assertEqual(
            mock.sentinel.code,
            self.get_source().getToken(tag))
