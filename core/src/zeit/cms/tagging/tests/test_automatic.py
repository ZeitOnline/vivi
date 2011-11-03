# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.tagging.interfaces import ITaggable
from zeit.cms.tagging.tag import Tag
from zeit.cms.testcontenttype.testcontenttype import TestContentType
import mock
import zeit.cms.testing


class AutomaticTagSourceTest(zeit.cms.testing.FunctionalTestCase):

    def test_values_combine_objects_keywords_and_disabled_keywords(self):
        content = TestContentType()
        content.keywords = (Tag('foo'),)
        content.disabled_keywords = (Tag('bar'),)
        source = ITaggable['keywords'].bind(content).value_type.source
        self.assertEqual((Tag('foo'), Tag('bar')), tuple(source))

    def test_update_sets_all_keywords_obtained_from_tagger(self):
        content = TestContentType()
        content.keywords = (Tag('foo'),)
        content.disabled_keywords = (Tag('bar'),)
        source = ITaggable['keywords'].bind(content).value_type.source
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger().return_value = (Tag('bar'), Tag('baz'))
            source.factory.update()  # XXX
        self.assertEqual((Tag('bar'), Tag('baz')), content.keywords)
