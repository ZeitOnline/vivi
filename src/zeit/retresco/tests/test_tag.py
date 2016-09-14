# coding: utf8
import zeit.cms.interfaces
import zeit.retresco.testing


class TagTest(zeit.retresco.testing.FunctionalTestCase):
    """Testing ..tag.Tag."""

    def test_from_code_generates_a_tag_object_equal_to_its_source(self):
        from ..tag import Tag
        tag = Tag(u'Vipraschül', 'Person')
        self.assertEqual(tag, Tag.from_code(tag.code))

    def test_uniqueId_from_tag_can_be_adapted_to_tag(self):
        from ..tag import Tag
        tag = Tag(u'Vipraschül', 'Person')
        self.assertEqual(tag, zeit.cms.interfaces.ICMSContent(tag.uniqueId))
